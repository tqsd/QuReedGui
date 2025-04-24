"""
Module containing BoardManager, one of the logic modules.
"""
from __future__ import annotations
import typing
from qureed_gui.logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from qureed_project_server import server_pb2

if typing.TYPE_CHECKING:
    from qureed_gui.components.board import Board, BoardBar, Info
    from qureed_gui.components.board_component import BoardComponent
    import flet as ft

LMH = LogicModuleHandler()

class BoardManager:
    """
    BoardManager (Singleton) manages the board and allow different
    parts of the QuReedGui to communicate with the board.

    Attributes:
    -----------
    board (ft.Control): actual board component
    opened_scheme (str): the name of currently displayed scheme
    board_bar (ft.Control): Board bar displays the name of the scheme
    board_info (ft.Control): Board info displays the information
       about device/port the user is currently hovering
    board_controls (ft.Control): Board controls (like + (add device))
    initialized (bool): Initialization flag, part of the Singleton Pattern

    Methods:
    --------
    register_board_bar(board_bar): Registers the board bar
    redister_board_info(board_info): Registers the board info element
    register_board(): Registers the board, which displays the scheme
    close_board(): Closes the scheme
    open_scheme(scheme): Opens existing scheme
    save_scheme(): Saves the current scheme
    add_device(device): Adds the device to the board/scheme
    remove_device(device): Removes the device from the board/scheme
    display_info(info): Displays information on the board_info
    center_board(): Centers the board
    explorer_expansion(width): Handles placement change when
        the file explorer width changes

    Examples:
    ---------
    Example of using this class in the QuReedGui context:
        >>> from qureed_gui.logic.logic_module_hangler import (
        >>>     LogicModuleHandler, LogicModuleEnum
        >>> )
        >>> BM = LogicModuleHandler().get_logic(
        >>>     LogicModuleEnum.BOARD_MANAGER
        >>> )
        >>> BM.center_board()
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BoardManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.board=None
            self.opened_scheme=None
            self.board_bar=None
            self.board_info=None
            self.board_controls=None
            LMH.register(LogicModuleEnum.BOARD_MANAGER, self)
            self.initialized=True

    @property
    def device_controls(self) -> list:
        """
        Returns all of the device controls currently on the board
        DEPRECATE?

        Returns:
        --------
        list[device_controls]
        """
        if self.board:
            return self.board.device_controls
        return []

    def register_board_bar(self, board_bar: BoardBar) -> None:
        """
        Registers the BoardBar for later reference

        Parameters:
        -----------
        board_bar (BoardBar): BoardBar instance
        """
        self.board_bar=board_bar

    def register_board_info(self, board_info: Info):
        """
        Registers the board info bar:

        Parameters:
        -----------
        board_info (Info): reference to the Info component of the board
        """
        self.board_info = board_info

    def register_board(self, board: Board):
        """
        Registers the flet board component for later reference

        Parameters:
        -----------
        board (Board): the board, which actually displays the scheme
        """
        self.board=board

    def close_scheme(self) -> None:
        """
        Clears the board and removes the name of the scheme.
        """
        self.opened_scheme = ""
        if self.board_bar:
            self.board_bar.update_scheme_name("No Scheme Opened")
        if self.board:
            self.board.clear_board()

    def open_scheme(self, scheme: str) -> None:
        """
        Opens the scheme and displays it on the board.
        The scheme is opened using the server (Server Manager),
        which loads the QuReed modules and returns the devices and
        connections.

        Parameters:
        -----------
        scheme (str): the name of the scheme
        """
        LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER).deselect_all()
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)

        if self.opened_scheme != scheme:
            self.save_scheme()
            self.board.clear_board()
            scheme_resp = SvM.open_scheme(scheme) 
            if scheme_resp.status == "success":
                self.opened_scheme = scheme
                if self.board_bar:
                    self.board_bar.update_scheme_name(self.opened_scheme)
                self.board.load_devices_bulk(scheme_resp.devices)
                self.board.load_connections_bulk(scheme_resp.connections)

    def save_scheme(self):
        """
        Saves the current scheme. It compiles the devices and their
        positions on the board and then sends the list to the server,
        which actually saves the scheme.
        """

        from components.board_component import BoardComponent
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        devices = []
        if not self.opened_scheme:
            return
        for device in self.device_controls:
            if not isinstance(device, BoardComponent):
                continue
            device_msg = device.device
            device_msg.location[:] = [device.left, device.top]
            devices.append(device_msg)

        response = SvM.save_scheme(
            board=self.opened_scheme,
            devices=devices
            )
        if response.status == "success":
            PM.display_message(f"{self.opened_scheme} succesfully saved")
        else:
            PM.display_message(
                f"Saving of Scheme {self.opened_scheme} failed: {response.message}"
                )

    def add_device(self, device:server_pb2.Device):
        """
        Adds a new device to the board.

        Parameters:
        -----------
        device (server_pb2.Device): Device message, which defines the device 
            on the board component
        """
        if self.board:
            print("adding a new device", device)
            new_device = server_pb2.Device()
            new_device.CopyFrom(device)
            self.board.add_device(new_device)

    def remove_device(self, device:BoardComponent):
        """
        Removes the device from the board, also notifies the server
        about the device removal.

        Parameters:
        -----------
        device (BoardComponent): The device to be removed
        """
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        response = SvM.remove_device(device.device.uuid)
        if response.status=="success":
            self.board.board.controls.remove(device)
            self.board.update()
            PM.display_message("Device succesfully removed")
            return
        PM.display_message(f"Device removal failed {response.message}")

    def display_info(self, info:str) -> None:
        """
        Displays some information (info) on the board info widget.

        Parameters:
        -----------
        info (str): information string to display
        """
        if self.board_info:
            self.board_info.update_info(info)

    def center_board(self, e:ft.TapEvent) -> None:
        """
        Centers the board. Board is moved to location (0,0)

        Parameters:
        -----------
        e (ft.TapEvent): Flet event, which triggers this action
        """
        self.board.center_board(e)

    def explorer_expansion(self, width:float):
        """
        Hook, triggered by the project explorer which updates
        the location of the board_bar and board_controls

        Parameters:
        -----------
        width (float): New width of the explorer
        """
        if self.board_bar:
            self.board_bar.left=width
            self.board_bar.update()
        if self.board_controls:
            self.board_controls.left=width
            self.board_controls.update()

    def reset_scroll(self):
        self.board.did_mount()
