#!/usr/bin/env python
import sys

import pygtk
pygtk.require('2.0')
import gtk
import gobject

frame_delay = 1000/60
frame_delays = [int(frame_delay * x) for x in (0.125, 0.25, 0.5, 0.75, 1, 2, 3, 4)]

def increase_delay(d):
    current = frame_delays.index(d)
    if current == len(frame_delays)-1:
        return d
    return frame_delays[current+1]

def decrease_delay(d):
    current = frame_delays.index(d)
    if current == 0:
        return d
    return frame_delays[current -1]

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
        self.image.connect('expose-event', self.on_image_expose)

        self.box.add(self.image)
        
        self.label = gtk.Label()
        self.label.set_justify(gtk.JUSTIFY_LEFT)

        hbox = gtk.HBox()
        hbox.pack_start(self.label, False, False)

        vbox = gtk.VBox()
        vbox.add(self.box)
        vbox.pack_start(hbox, False, False)

        self.window.add(vbox)

        for w in self.image, self.box, self.label, hbox, vbox, self.window:
            w.show()

        (self.box_width, self.box_height) = (self.box.allocation.width, self.box.allocation.height)
        self.cache = {}

        self.frame_delay = frame_delay
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
        self.displayed_file = None
        self.filename=""

        self.playing = False
        self.loop = False
        self.autoreverse = False
        self.skip = 1
        self.was_playing = "forwards"
        self.playing = False

        self.play_start()
        gtk.main()

    def update_status(self):
        label = "Loop: %s. Autoreverse: %s. Delay: %s. Skip: %s. File: %s" % (self.loop, self.autoreverse, self.frame_delay, self.skip, self.filename)
        self.label.set_text(label)

    def play_start(self):
        self.timer = gobject.timeout_add(200, self.play, 0)

    def play(self, image=0):
        self.playing="forwards"
        gobject.source_remove(self.timer)
        self.show_image_by_num(image)
        if image+self.skip < self.last_image:
            self.timer = gobject.timeout_add(self.frame_delay, self.play, image+self.skip)
        else :
            self.playing = None
            if self.loop:
                if self.autoreverse:
                    self.play_backwards()
                else:
                    self.play()

    play_forwards = play

    def play_backwards(self, image="last"):
        self.playing="backwards"
        gobject.source_remove(self.timer)
        if image == "last":
            image = self.last_image

        self.show_image_by_num(image)

        if image - self.skip >= 0:
            self.timer = gobject.timeout_add(self.frame_delay, self.play_backwards, image-self.skip)
        else :
            self.playing = None
            if self.loop:
                if self.autoreverse:
                    self.play()
                else:
                    self.play_backwards()

    def stop(self):
        self.was_playing = self.playing
        self.playing = False
        gobject.source_remove(self.timer)

    def show_image(self, filename):
        buf = self.cache.get(filename)
        if not buf:
            buf = gtk.gdk.pixbuf_new_from_file_at_size(filename, self.box.allocation.width, self.box.allocation.height)
            self.cache[filename] = buf
        self.image.set_from_pixbuf(buf)
        self.filename = filename
        self.update_status()

    def show_image_by_num(self, num):
        if num == self.displayed_file:
            return
        if num < 0 or num > self.last_image:
            return
        #print 'showing', num, 'out of', self.len-1
        self.displayed_file = num
        self.show_image(self.images[num])


    def click(self, widget, event):
        if event.button == 1:
            self.show_image_by_num(self.displayed_file+self.skip)
        else:
            self.show_image_by_num(self.displayed_file-self.skip)

    def motion_notify_event(self, widget, event):
        gobject.source_remove(self.timer)
        w =  widget.allocation.width
        x = event.x
        if x < 0:
            x=0
        if x >= w:
            x = w
        image_num = int(self.last_image * x / w)
        image_num = (image_num/self.skip)*self.skip #align on a skip boundry
        self.show_image_by_num(image_num)

    def type(self, widget, event):
        file_to_play = self.displayed_file
        if event.keyval == gtk.keysyms.space:
            self.handle_pause()
        if event.keyval in (gtk.keysyms.Right, gtk.keysyms.p):
            if file_to_play == self.last_image:
                file_to_play = 0
            self.play(file_to_play)

        if event.keyval == gtk.keysyms.Left:
            if file_to_play == 0:
                file_to_play = self.last_image
            self.play_backwards(file_to_play)

        if event.keyval == gtk.keysyms.l:
            self.loop = not self.loop

        if event.keyval == gtk.keysyms.r:
            self.autoreverse = not self.autoreverse
            if self.autoreverse:
                self.loop = True

        if event.keyval == gtk.keysyms.Up:
            self.frame_delay = increase_delay(self.frame_delay)
        if event.keyval == gtk.keysyms.Down:
            self.frame_delay = decrease_delay(self.frame_delay)

        if event.keyval == gtk.keysyms.bracketleft:
            if self.skip !=1:
                self.skip = self.skip/2
        if event.keyval == gtk.keysyms.bracketright:
            if self.skip !=32:
                self.skip = self.skip*2
        self.update_status()

    def handle_pause(self):
        if self.playing:
            self.stop()
        else:
            getattr(self, 'play_' + self.was_playing)(self.displayed_file)

    def on_image_expose(self, widget, event):
        if (self.box_width, self.box_height) != (self.box.allocation.width, self.box.allocation.height):
            self.cache = {}
            self.show_image(self.images[self.displayed_file or 0])
        (self.box_width, self.box_height) = (self.box.allocation.width, self.box.allocation.height)

if __name__ == "__main__":
    images = sys.argv[1:]
    s = Scrubber()
    s.main(images)
