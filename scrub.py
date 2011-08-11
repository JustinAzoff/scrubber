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
        self.window.connect("key_press_event", self.type)

        self.image = gtk.Image()

        self.box.add(self.image)

        self.window.add(self.box)

        self.image.show()
        self.box.show()
        self.window.show()

        self.cache = {}

        self.frame_delay = 1000/60
        self.timer = None

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self, images):
        self.images = images# + list(reversed(images))
        self.pos = 0
        self.len = len(images)
        self.last_image = self.len - 1
        self.displayed_file = 0

        self.playing = False
        self.loop = False
        self.autoreverse = False

        self.play_start()
        gtk.main()

    def play_start(self):
        self.timer = gobject.timeout_add(200, self.play, 0)

    def play(self, image=0):
        gobject.source_remove(self.timer)
        self.show_image_by_num(image)
        if image < self.last_image:
            self.timer = gobject.timeout_add(self.frame_delay, self.play, image+1)
        else :
            if self.loop:
                if self.autoreverse:
                    self.play_backwards()
                else:
                    self.play()

    def play_backwards(self, image="last"):
        gobject.source_remove(self.timer)
        if image == "last":
            image = self.last_image

        self.show_image_by_num(image)

        if image != 0:
            self.timer = gobject.timeout_add(self.frame_delay, self.play_backwards, image-1)
        else :
            if self.loop:
                if self.autoreverse:
                    self.play()
                else:
                    self.play_backwards()


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
        if num < 0 or num > self.last_image:
            return
        #print 'showing', 1+num, 'out of', self.len
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
        image_num = int(self.last_image * x / w)
        self.show_image_by_num(image_num)

    def type(self, widget, event):
        file_to_play = self.displayed_file
        if event.keyval in (gtk.keysyms.Right, gtk.keysyms.space, gtk.keysyms.p):
            if file_to_play == self.last_image:
                file_to_play = 0
            self.play(file_to_play)
            return

        if event.keyval == gtk.keysyms.Left:
            if file_to_play == 0:
                file_to_play = self.last_image
            self.play_backwards(file_to_play)
            return

        if event.keyval == gtk.keysyms.l:
            self.loop = not self.loop
            return

        if event.keyval == gtk.keysyms.r:
            self.autoreverse = not self.autoreverse
            if self.autoreverse:
                self.loop = True
            return

        if event.keyval == gtk.keysyms.Up:
            self.frame_delay += 100
        if event.keyval == gtk.keysyms.Down:
            self.frame_delay -= 100
        if self.frame_delay <=0:
            self.frame_delay = 10

if __name__ == "__main__":
    images = sys.argv[1:]
    s = Scrubber()
    s.main(images)
