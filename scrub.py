#!/usr/bin/env python
import sys

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class Scrubber:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        self.box = gtk.EventBox()


        self.box.connect("motion_notify_event", self.motion_notify_event)
        self.box.connect("button_press_event", self.click)

        self.image = gtk.Image()

        self.box.add(self.image)

        self.window.add(self.box)

        self.image.show()
        self.box.show()
        self.window.show()

        self.cache = {}

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self, images):
        self.images = images# + list(reversed(images))
        self.pos = 0
        self.len = len(images)
        self.displayed_file = 0
        gtk.main()


    def show_image(self, filename):
        buf = self.cache.get(filename)
        if not buf:
            buf = gtk.gdk.pixbuf_new_from_file_at_size(filename, self.box.allocation.width, self.box.allocation.height)
            self.cache[filename] = buf
        self.image.set_from_pixbuf(buf)
        self.filename = filename

    def show_image_by_num(self, num):
        if num == self.displayed_file:
            return
        if num < 0 or num >= self.len:
            return
        print 'showing', 1+num, 'out of', self.len
        self.displayed_file = num
        self.show_image(self.images[num])


    def click(self, widget, event):
        if event.button == 1:
            self.show_image_by_num(self.displayed_file+1)
        else:
            self.show_image_by_num(self.displayed_file-1)

    def motion_notify_event(self, widget, event):
        w =  widget.allocation.width
        x = event.x
        if x < 0:
            x=0
        if x >= w:
            x = w
        image_num = int((self.len-1) * x / w)
        self.show_image_by_num(image_num)


if __name__ == "__main__":
    images = sys.argv[1:]
    s = Scrubber()
    s.main(images)
