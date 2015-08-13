#!/usr/bin/env python3

from gi.repository import Gtk
from gi.repository import GObject
import argparse


class BreakWindow(Gtk.Window):
    def __init__(self, period_timer):
        Gtk.Window.__init__(self, title="Take a break")

        self.period_timer = period_timer
        self.rest = self.period_timer.break_time
        self.timeout_id = None

        # window markup
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_modal(True)
        self.set_keep_above(True)
        self.set_border_width(10)

        # box markup
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.set_size_request(200, 60)
        self.add(self.box)

        # label with rest time
        self.label = Gtk.Label()
        self.set_label_text()
        self.box.pack_start(self.label, True, True, 0)

        # button to interrupt timeout
        self.interrupt_button = Gtk.Button(label="Interrupt a break")
        self.interrupt_button.connect("clicked", self.on_interrupt_clicked)
        self.box.pack_start(self.interrupt_button, True, True, 0)

        # run timeout
        self.add_timeout()

    def add_timeout(self):
        self.timeout_id = GObject.timeout_add(1000, self.on_timeout, None)

    def remove_timeout(self):
        GObject.source_remove(self.timeout_id)

    def end_break(self):
        self.remove_timeout()
        self.period_timer.add_timeout()
        self.destroy()

    def on_interrupt_clicked(self, data):
        self.end_break()

    def set_label_text(self):
        self.label.set_text("Left to rest %s seconds!" % self.rest)

    def on_timeout(self, data):
        self.rest -= 1
        self.set_label_text()
        if self.rest > 0:
            return True
        else:
            self.end_break()
            return False


class PeriodTimer:
    def __init__(self, period_time, break_time):
        self.period_time = period_time
        self.break_time = break_time

        self.timeout_id = None
        self.add_timeout()

    def add_timeout(self):
        self.timeout_id = GObject.timeout_add(self.period_time * 1000, self.on_timeout, None)

    def remove_timeout(self):
        GObject.source_remove(self.timeout_id)
        self.timeout_id = None

    def show_break_window(self, data):
        if self.timeout_id is not None:
            self.remove_timeout()
            break_window = BreakWindow(self)
            break_window.show_all()

    def on_timeout(self, data):
        self.show_break_window(data)


# Argument parser
parser = argparse.ArgumentParser(description='Small program to take breaks.')
parser.add_argument('--period-time', type=int, required=True, help='period time between breaks in seconds')
parser.add_argument('--break-time', type=int, required=True, help='break time in seconds')
args = parser.parse_args()


# Period timer
period_timer = PeriodTimer(args.period_time, args.break_time)


# Menu

menu = Gtk.Menu()
menu_item_break = Gtk.MenuItem(label="Take a break")
menu_item_break.connect("activate", period_timer.show_break_window)
menu.append(menu_item_break)
menu_item_quit = Gtk.MenuItem(label="Quit")
menu_item_quit.connect("activate", lambda q: Gtk.main_quit())
menu.append(menu_item_quit)


# Status icon

def popup_menu(icon, button, time):
    menu.show_all()
    menu.popup(None, None, None, None, button, time)


status_icon = Gtk.StatusIcon()
status_icon.set_from_stock(Gtk.STOCK_EXECUTE)
status_icon.set_title("StatusIcon")
status_icon.connect("popup-menu", popup_menu)

Gtk.main()
