#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject, GdkPixbuf
import string
import os
import re
import cairo
import time
import sys
import urllib

from menu import CreateFullMenu
from preferences_dialog import PreferencesDialog
from document import BEditDocument
		
class TextViewWindow(Gtk.Window):
	"""程序的主要部分"""
	
	history = []
	historyListRange = 10
	
	def __init__(self):
		Gtk.Window.__init__(self, title="带背景的文本编辑器")
		
		GObject.signal_new("changed", BEditDocument, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())	
		
		
		self.grid = Gtk.Grid()
		self.add(self.grid)
		
		#载入历史记录
		self.load_config()
		self.set_default_size(self.sizeWidth, self.sizeHeight)
        
		self.create_notebook()
		self.create_menubar()
		self.create_toolbar()
		self.create_find()
		
		self.on_new()
		self.set_style()
		# 图标来自 http://www.iconlet.com/info/85512_gedit-icon_128x128
		self.set_icon_from_file(sys.path[0]+"/icons/bedit.png")

	def create_toolbar(self):
		"""建立工具栏，这里的工具栏，实际上是选项卡上的一些标签页。"""
		
		self.button = [Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW),
				Gtk.MenuToolButton.new_from_stock(Gtk.STOCK_OPEN),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_SAVE),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_PRINT),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDO),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_REDO),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_CUT),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_COPY),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_PASTE),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_FIND),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_PREFERENCES)]
				
		tool_box = Gtk.HBox()
		for i in self.button:
			tool_box.pack_start(i, False, False, 0)
		tool_box.show_all()
		self.notebook.append_page(Gtk.Box(spacing=6), tool_box)
				
		self.button[0].connect("clicked", self.on_new)
		self.button[1].connect("clicked", self.on_open_file)
		self.button[2].connect("clicked", self.on_save)
		self.button[4].connect("clicked", self.on_undo)
		self.button[5].connect("clicked", self.on_redo)
		self.button[9].connect("clicked", self.on_find)
		self.button[-1].connect("clicked", self.on_preferences)
		
		#历史记录
		historymenu = Gtk.Menu()
		for i in self.history:
			new = Gtk.MenuItem.new_with_label(i)
			historymenu.append(new)
			new.show()
			new.connect("activate", self.open_with_menu)
		self.button[1].set_menu(historymenu)
		self.notebook.popup_enable()
		
	def create_menubar(self):
		"""建立一个菜单栏"""
		self.menubar = CreateFullMenu(self, self.history)
		self.grid.attach(self.menubar, 0, 0, 1, 1)
		
	def create_find(self):
		self.findFindText = Gtk.Entry()
		self.findReplaceText = Gtk.Entry()
		self.frameBox = Gtk.HBox()
		button = Gtk.Button()
		button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
		button.connect("clicked", self.close_find)
		self.frameBox.pack_start(button, False, False, 0)
		self.frameBox.pack_start(Gtk.Label("查找："), False, False, 0)
		self.frameBox.pack_start(self.findFindText, False, False, 0)
		buttonPrev = Gtk.Button("上一个")
		buttonNext = Gtk.Button("下一个")
		buttonPrev.connect("clicked", self.find)
		buttonNext.connect("clicked", self.find)
		self.frameBox.pack_start(buttonPrev, False, False, 0)
		self.frameBox.pack_start(buttonNext, False, False, 0)
		self.frameBox.pack_start(Gtk.Label("替换："), False, False, 0)
		self.frameBox.pack_start(self.findReplaceText, False, False, 0)
		buttonAllReplace = Gtk.Button("全部替换")
		buttonReplace = Gtk.Button("替换")
		buttonAllReplace.connect("clicked", self.all_replace)
		buttonReplace.connect("clicked", self.replace)
		self.frameBox.pack_start(buttonAllReplace, False, False, 0)
		self.frameBox.pack_start(buttonReplace, False, False, 0)
		self.grid.attach(self.frameBox, 0, 2, 1, 1)
		
	def set_language(self, menu = None, language = None):
		src_buffer = self.get_buffer()
		
		manager = GtkSource.LanguageManager()
		src_buffer.set_language(manager.get_language(language))
		self.get_document().language = language
		
		self.on_update_title()
		
	def open_with_menu(self, menu = None):
		"""通过历史菜单打开文件"""
		# 判断最后一个标签里面是否是空文档
		last_doc = self.notebook.get_nth_page(-1).get_child()
		if last_doc.filename != "无标题文档" or last_doc.change_number > 0 or last_doc.stext != "":
			self.on_new()
			last_doc = self.notebook.get_nth_page(-1).get_child()
		last_doc.open(menu.get_label())
		self.append_history(menu.get_label())
		self.save_config()
						
	def create_notebook(self):
		"""建立选项卡"""
		self.notebook = Gtk.Notebook()
		self.grid.attach(self.notebook, 0, 1, 1, 1)
		    
	def on_new(self, widget = None):
		"""在这里新建一个文档"""
		new_textview = BEditDocument()
		new_textview.connect("changed", self.on_update_title)
		#拖放
		new_textview.connect("drag-data-received", self.drag_data)
		new_scrolledwindow = Gtk.ScrolledWindow()
		new_scrolledwindow.set_hexpand(True)
		new_scrolledwindow.set_vexpand(True)
		new_scrolledwindow.add(new_textview)			
		
		tab_box = self.new_label_with_icon_and_close_button("无标题文档", "python", new_scrolledwindow)
		self.notebook.append_page(new_scrolledwindow, tab_box)
		tab_box.show_all()
		#切换到刚插入的一页
		self.show_all()
		self.notebook.set_current_page(self.notebook.get_n_pages()-1)
		
	def new_label_with_icon_and_close_button(self, label="", language="python", close_object=None):
	
		new_icon = Gtk.Image.new_from_file(sys.path[0]+"/icons/"+language+".png")
		new_label = Gtk.Label(label)
		button = Gtk.Button()
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.set_focus_on_click(False)
		button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
		button.connect("clicked", self.close_self, close_object)
		tab_box = Gtk.HBox()
		tab_box.pack_start(new_icon, False, False, 0)
		tab_box.pack_start(new_label, True, True, 0)
		tab_box.pack_start(button, False, False, 0)
		return tab_box
		    
	def on_open_file(self, widget):
		dialog = Gtk.FileChooserDialog("打开文件", self,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
			 
		self.add_filters(dialog)
				
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
		
			self.open_with_filename(dialog.get_filename())
			
		dialog.destroy()
		
	def on_save(self, widget = None):
		cur_wid = self.notebook.get_nth_page(self.notebook.get_current_page()).get_child()
		# 判断文件是否有文件名
		if cur_wid.filepath == "":
			self.on_update_title()
			return self.on_save_as(widget)
		else:
			# 直接使用已经存在的文件名
			filename = cur_wid.save()
			self.append_history(filename)
			self.save_config()
			self.on_update_title()
			# 如果保存正确则返回 True
			return True
			
	def on_save_as(self, widget = None):
		"""显示另存为对话框"""
		cur_wid = self.notebook.get_nth_page(self.notebook.get_current_page()).get_child()
		dialog = Gtk.FileChooserDialog("另存为", self,
			Gtk.FileChooserAction.SAVE,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
			 
		self.add_filters(dialog)
				
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			cur_wid.save(dialog.get_filename())
			self.append_history(dialog.get_filename())
			self.save_config()
			dialog.destroy()
			return True
		dialog.destroy()
		return False
		
	def on_revert_to_saved(self, widget = None):
		cur_wid = self.notebook.get_nth_page(self.notebook.get_current_page()).get_child()
		if cur_wid.change_number != 0:
			dialog = Gtk.MessageDialog(
				type=Gtk.MessageType.QUESTION, 
				message_format=
					'在关闭前将更改保存到文档“'+ 
					cur_wid.filename+
					'”吗？'
			)
			dialog.format_secondary_text(
				"如果您不保存，前 "+
				str((time.time()-cur_wid.change_timestamp+50)//60)[:-2]+
				" 分钟内对文档所作的更改将永久丢失。"
			)
			dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
			dialog.add_button(Gtk.STOCK_REVERT_TO_SAVED, Gtk.ResponseType.OK)
			if dialog.run() == Gtk.ResponseType.OK:
				cur_wid.revert_to_saved()
			dialog.destroy()
		
	def on_close(self, widget = None):
		"""关闭标签"""
		num = self.notebook.get_current_page()
		cur_wid = self.notebook.get_nth_page(num).get_child()
		# 检查文件时否保存
		if cur_wid.change_number > 0:
			dialog = Gtk.MessageDialog(
				type=Gtk.MessageType.QUESTION, 
				message_format=
					'是否放弃对文档"'+
					cur_wid.filename+
					'"所有的未保存更改？'
			)
			dialog.format_secondary_text(
				"之前 "+
				str((time.time()-cur_wid.change_timestamp+50)//60)[:-2]+
				" 分钟内对文档所作的更改将永久丢失。"
			)
			dialog.add_button("放弃更改并退出", Gtk.ResponseType.NO)
			dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
			dialog.add_button(Gtk.STOCK_SAVE_AS, Gtk.ResponseType.YES)
			response = dialog.run()
			if response == Gtk.ResponseType.NO:
				self.notebook.remove_page(num)
			elif response == Gtk.ResponseType.YES:
				if self.on_save():
					self.notebook.remove_page(num)
			dialog.destroy()
		else:
			self.notebook.remove_page(num)
			
	def close_self(self, button, data=None):
		self.notebook.remove_page(self.notebook.page_num(data))
		
	def on_undo(self, menu):
		"""撤销"""
		num = self.notebook.get_current_page()
		cur_wid = self.notebook.get_nth_page(num).get_child()
		if cur_wid.get_buffer().can_undo():
			cur_wid.get_buffer().undo()
		
	def on_redo(self, menu):
		"""重做"""
		num = self.notebook.get_current_page()
		cur_wid = self.notebook.get_nth_page(num).get_child()
		if cur_wid.get_buffer().can_redo():
			cur_wid.get_buffer().redo()
		
	def on_find(self, widget = None):
		"""搜索命令"""
		self.frameBox.show_all()
		
	def close_find(self, widget):
		self.frameBox.hide()
		
	def on_preferences(self, widget = None):
		"""显示属性对话框"""
		
		dialog = PreferencesDialog(self)
		
		#还要从 css 中读取属性
		file_object = open(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css")
		try:
			text = file_object.read()
			# 将 css 文本交给对话框处理
			dialog.set_css(text)
		finally:
			file_object.close()
		#写入其他内容
		dialog.set_historyListRange(self.historyListRange)
				
		response = dialog.run()
		
		file_object = open(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css","w")
		try:
			file_object.write(dialog.get_css())
		finally:
			file_object.close()
		
		#读取内容
		self.historyListRange = dialog.get_historyListRange()
		dialog.destroy()
		
		#更新样式
		self.set_style()
		
	def on_update_title(self, widget = None):
		"""更新标题栏"""
		cw = self.notebook.get_nth_page(self.notebook.get_current_page())
		cwt = cw.get_child()
		if cwt.change_number == 0:
						
			self.set_title(cwt.filename+" ("+cwt.filepath+") - bedit")
			tab_box = self.new_label_with_icon_and_close_button(cwt.filename, cwt.language, cw)
			self.notebook.set_tab_label(cw, tab_box)
			tab_box.show_all()
		else:
			self.set_title("*" + cwt.filename+" ("+cwt.filepath+") - bedit")
			tab_box = self.new_label_with_icon_and_close_button("*"+cwt.filename, cwt.language, cw)
			self.notebook.set_tab_label(cw, tab_box)
			tab_box.show_all()
				
	def add_filters(self, dialog):
		filter_text = Gtk.FileFilter()
		filter_text.set_name("文本文件")
		filter_text.add_mime_type("text/plain")
		dialog.add_filter(filter_text)
		
		filter_py = Gtk.FileFilter()
		filter_py.set_name("Python 文件")
		filter_py.add_mime_type("text/x-python")
		dialog.add_filter(filter_py)
		
		filter_any = Gtk.FileFilter()
		filter_any.set_name("所有文件")
		filter_any.add_mime_type("*")
		dialog.add_filter(filter_any)
		
	def set_style(self):
		"""用来设置外观"""
		
		style_provider = Gtk.CssProvider()
		style_provider.load_from_path(os.environ['HOME']+'/.local/share/bedit/gtk-widgets3.css')
		Gtk.StyleContext.add_provider_for_screen(
			Gdk.Screen.get_default(),
			style_provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
			
	def load_config(self):
		file_object = open(os.environ['HOME']+"/.local/share/bedit/config")
		try:
			for eachline in file_object:
				els = eachline.split()
				if els[0] == "wrap_mode":
				#读取换行模式
					if els[1] == "NONE":
						self.wrap_mode = Gtk.WrapMode.NONE
					if els[1] == "CHAR":
						self.wrap_mode = Gtk.WrapMode.CHAR
					if els[1] == "WORD":
						self.wrap_mode = Gtk.WrapMode.WORD
					if els[1] == "WORD_CHAR":
						self.wrap_mode = Gtk.WrapMode.WORD_CHAR
				elif els[0] == "width":
				#读取窗口的长宽
					self.sizeWidth = string.atoi(els[1])
				elif els[0] == "height":
					self.sizeHeight = string.atoi(els[1])
				elif els[0] == "historyListRange":
				#历史列表长度
					self.historyListRange = string.atoi(els[1])
				else:
				#读取历史记录
					self.history.append(eachline.strip('\n'))
		finally:
			file_object.close()
			
	def save_config(self):
		file_object = open(os.environ['HOME']+"/.local/share/bedit/config","w")
		try:
			if self.wrap_mode == Gtk.WrapMode.NONE:
				file_object.write("wrap_mode NONE\n")
			elif self.wrap_mode == Gtk.WrapMode.CHAR:
				file_object.write("wrap_mode CHAR\n")
			elif self.wrap_mode == Gtk.WrapMode.WORD:
				file_object.write("wrap_mode WORD\n")
			elif self.wrap_mode == Gtk.WrapMode.WORD_CHAR:
				file_object.write("wrap_mode WORD_CHAR\n")
				
			#保存大小
			width, height = self.get_size()
			file_object.write("width "+str(width)+"\n")
			file_object.write("height "+str(height)+"\n")
			file_object.write("historyListRange "+str(self.historyListRange)+"\n")

			for eachline in self.history:
				file_object.write(eachline+'\n')
		finally:
			file_object.close()
			
	def main_quit(self, widget, event, data=None):
		self.save_config()
		Gtk.main_quit()
		
	def append_history(self, file):
		filemenu = self.menubar.get_children()[0].get_submenu()
		toolmenu = self.button[1].get_menu()
		if file in self.history:
			self.history.remove(file)
			#还要从文件菜单中移除
			for i in filemenu.get_children():
				if i.get_label() == file:
					filemenu.remove(i)
			for i in toolmenu.get_children():
				if i.get_label() == file:
					toolmenu.remove(i)
			#插入菜单
			new1 = Gtk.MenuItem.new_with_label(file)
			new2 = Gtk.MenuItem.new_with_label(file)
			filemenu.insert(new1,10)
			toolmenu.insert(new2,0)
			new1.show()
			new2.show()
			new1.connect("activate", self.open_with_menu)
			new2.connect("activate", self.open_with_menu)
		self.history.insert(0,file)
		self.history = self.history[0:self.historyListRange]
		
	def find(self, button = None):
		b = self.get_buffer()
		#搜索“上一个”和搜索“下一个”的区别在使用 start.forward_search 和 end.backward_search。
		if button == None or button.get_label() == "下一个":
			area = self.get_document().find(self.findFindText.get_text(), "下一个")
		else:
			area = self.get_document().find(self.findFindText.get_text(), "上一个")
		# 获得选中位置的坐标，并且将滚动条滚动到这个位置。
		adjustment = self.get_scrolledwindow().get_vadjustment()
		adjustment.set_value(area.y - adjustment.get_page_size()/2)
		self.get_scrolledwindow().set_vadjustment(adjustment)
	def replace(self, button):
		d = self.get_document()
		if d.match_start:
			n = self.escape(self.findReplaceText.get_text())
			b = self.get_buffer()
			# 删除选中的部分
			b.delete(self.match_start, self.match_end)
			# 插入新内容
			b.insert_at_cursor(n)
			self.find()
			
	def all_replace(self, button):
		"""全文替换"""
		self.get_document().all_replace(self.escape(self.findFindText.get_text()),self.escape(self.findReplaceText.get_text()))
		
	def drag_data(self, widget, context, x, y, data, info, time):
		files = data.get_text().rstrip('\n').split('\n')
		for fn in files:
			self.open_with_filename(urllib.unquote(fn[7:-1]))
		
	def open_with_filename(self, name):
		# 判断最后一个标签里面是否是空文档
		last_doc = self.notebook.get_nth_page(-1).get_child()
		if last_doc.filename != "无标题文档" or last_doc.change_number > 0 or last_doc.stext != "":
			self.on_new()
			last_doc = self.notebook.get_nth_page(-1).get_child()
		last_doc.open(name)
		self.append_history(name)
		self.save_config()
		
	def get_buffer(self):
		cw = self.notebook.get_nth_page(self.notebook.get_current_page())
		src_view = cw.get_child()
		return src_view.get_buffer()
		
	def get_document(self):
		cw = self.notebook.get_nth_page(self.notebook.get_current_page())
		src_view = cw.get_child()
		return src_view
		
	def get_scrolledwindow(self):
		return self.notebook.get_nth_page(self.notebook.get_current_page())
		
	def escape(self, string):
		"""手动转换"""
		n = string.replace('\\n','\n')
		n = n.replace('\\t','\t')
		n = n.replace('\\v','\v')
		n = n.replace('\\0','\0')
		return n
		
if __name__ == "__main__":
	# 如果目录不存在则建立目录
	if not os.path.exists(os.environ['HOME']+"/.local"):
		os.mkdir(os.environ['HOME']+"/.local")
	if not os.path.exists(os.environ['HOME']+"/.local/share"):
		os.mkdir(os.environ['HOME']+"/.local/share")
	if not os.path.exists(os.environ['HOME']+"/.local/share/bedit"):
		os.mkdir(os.environ['HOME']+"/.local/share/bedit")
	# 如果文件不存在则建立文件
	if not os.path.isfile(os.environ['HOME']+"/.local/share/bedit/config"):
		file_object = open(os.environ['HOME']+"/.local/share/bedit/config", "w")
		try:
			file_object.write("width 720\nheight 890")
		finally:
			file_object.close()
	if not os.path.isfile(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css"):
		file_object = open(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css", "w")
		try:
			file_object.write("GtkNotebook{background-color:#FFF);}\nGtkScrolledWindow,GtkSourceView{background-color:#000;}\nGtkSourceView:selected{background-color:#C80;}\nGtkSourceView{font:文泉驿等宽微米黑 13;}")
		finally:
			file_object.close()
	
	
	win = TextViewWindow()
	win.connect("delete-event", win.main_quit)
	#win.show_all()
	Gtk.main()
