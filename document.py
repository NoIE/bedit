#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject, GdkPixbuf
import time
import os

class BEditDocument(GtkSource.View):
	"""为 GtkSource.View 添加一些原来没有的东西。"""
	def __init__(self):
		GtkSource.View.__init__(self)
		self.filename = "无标题文档"
		self.filepath = ""
		self.stext = ""
		self.change_number = 0
		self.change_timestamp = time.time()
		self.language = "text"
			
		language = GtkSource.LanguageManager.get_default().get_language("python")
		buffer = GtkSource.Buffer.new_with_language(language)
		self.set_buffer(buffer)
		#修改后的信号
		buffer.connect("changed", self.text_change)
		self.load_config()
		
		self.buffer = GtkSource.Buffer()
		self.sourceview = GtkSource.View.new_with_buffer(self.buffer)
		
		self.tag_found = self.get_buffer().create_tag("found",background="yellow")
		
		
	def text_change(self, buffer):
		text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
		if self.stext == text:
			if self.change_number > 0:
				self.change_number = 0
				self.change_timestamp = time.time()
				#发出改变标题栏的信号
				self.emit('changed')
		#如果被修改了
		else:
			self.change_number = self.change_number+1
			if self.change_number == 1:
				self.emit('changed')
				
	def open(self, filename):
		# 在这里读取文件
		file_object = open(filename)
		try:
			self.stext = file_object.read()
			self.get_buffer().set_text(self.stext)
			# 将绝对路径分解成路径和文件名
			self.filepath , self.filename =  os.path.split(filename)
			self.emit('changed')
		finally:
			file_object.close()
			
	def save(self, filename = ""):
		"""在这里保存文件"""
		if filename == "":
			file_object = open(self.filepath + "/" + self.filename, 'w')
		else:
			file_object = open(filename, 'w')
			self.filepath , self.filename =  os.path.split(filename)
		try:
			self.stext = self.get_buffer().get_text(self.get_buffer().get_start_iter(), self.get_buffer().get_end_iter(), False)
			file_object.write(self.stext)
			# 将绝对路径分解成路径和文件名
			self.change_number = 0
			self.change_timestamp = time.time()
			self.emit('changed')
		finally:
			file_object.close()
			
		return self.filepath + "/" + self.filename
			
	def load_config(self):
		"""读取配置文件"""
		file_object = open(os.environ['HOME']+"/.local/share/bedit/config")
		try:
			for eachline in file_object:
				els = eachline.split()
				if els[0] == "wrap_mode":
					if els[1] == "NONE":
						self.set_wrap_mode(Gtk.WrapMode.NONE)
					if els[1] == "CHAR":
						self.set_wrap_mode(Gtk.WrapMode.CHAR)
					if els[1] == "WORD":
						self.set_wrap_mode(Gtk.WrapMode.WORD)
					if els[1] == "WORD_CHAR":
						self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
		finally:
			file_object.close()
		
	def revert_to_saved(self):
		"""恢复为最后一次保存的内容"""
		self.get_buffer().set_text(self.stext)
		self.change_number = 0
		self.change_timestamp = time.time()
		self.emit('changed')
