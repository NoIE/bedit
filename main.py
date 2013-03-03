#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject, GdkPixbuf
import string
import os
import re
import cairo
import time

from menu import CreateFullMenu
from preferences_dialog import PreferencesDialog
from document import BEditDocument

class SearchDialog(Gtk.Dialog):
	"""这里是一个在文本中搜索字符串的对话框。"""
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Search", parent,
			Gtk.DialogFlags.MODAL, buttons=(
				Gtk.STOCK_FIND, Gtk.ResponseType.OK,
				Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
			)
		)
		
		box = self.get_content_area()
		
		box.add(Gtk.Label("查找："))
		
		self.entry = Gtk.Entry()
		box.add(self.entry)
		
		self.show_all()
		
class TextViewWindow(Gtk.Window):
	"""程序的主要部分"""
	
	history = []
	
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
		
		self.on_new()
		self.set_style()

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
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_FIND_AND_REPLACE),
				Gtk.ToolButton.new_from_stock(Gtk.STOCK_PREFERENCES)]
				
		#toolbar = Gtk.Toolbar()
		tool_box = Gtk.HBox()
		for i in self.button:
			#toolbar.insert(i,0)
			tool_box.pack_start(i, False, False, 4)
		#toolbar.show_all()
		tool_box.show_all()
		#self.notebook.append_page(Gtk.Box(spacing=6), toolbar)
		self.notebook.append_page(Gtk.Box(spacing=6), tool_box)
				
		self.button[0].connect("clicked", self.on_new)
		self.button[1].connect("clicked", self.on_open_file)
		self.button[2].connect("clicked", self.on_save)
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
		
	def set_language(self, menu = None):
		language = menu.get_label()
		cw = self.notebook.get_nth_page(self.notebook.get_current_page())
		src_view = cw.get_child()
		src_buffer = src_view.get_buffer()
		
		manager = GtkSource.LanguageManager()
		
		src_buffer.set_language(manager.get_language(language))
		src_view.language = language
		
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
	
		new_icon = Gtk.Image.new_from_file("icons/"+language+".png")
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
			# 判断最后一个标签里面是否是空文档
			last_doc = self.notebook.get_nth_page(-1).get_child()
			if last_doc.filename != "无标题文档" or last_doc.change_number > 0 or last_doc.stext != "":
				self.on_new()
				last_doc = self.notebook.get_nth_page(-1).get_child()
			last_doc.open(dialog.get_filename())
			self.append_history(dialog.get_filename())
			self.save_config()
			
		dialog.destroy()
		
	def on_save(self, widget = None):
		cur_wid = self.notebook.get_nth_page(self.notebook.get_current_page()).get_child()
		# 判断文件是否有文件名
		if cur_wid.filepath == "":
			return self.on_save_as(widget)
		else:
			# 直接使用已经存在的文件名
			filename = cur_wid.save()
			self.append_history(filename)
			self.save_config()
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
					'”吗？',
				buttons = (Gtk.Button("放弃更改并退出"),Gtk.ButtonsType.OK_CANCEL)
			)
			dialog.format_secondary_text(
				"如果您不保存，前 "+
				str((time.time()-cur_wid.change_timestamp+50)//60)[:-2]+
				" 分钟内对文档所作的更改将永久丢失。"
			)
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
		
	def on_find(self, widget = None):
		dialog = SearchDialog(self)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			cursor_textbuffer = self.notebook.get_nth_page(self.notebook.get_current_page()).get_child().get_buffer()
			cursor_mark = cursor_textbuffer.get_insert()
			start = cursor_textbuffer.get_iter_at_mark(cursor_mark)
			if start.get_offset() == self.textbuffer.get_char_count():
				start = self.textbuffer.get_start_iter()
				
			self.search_and_mark(dialog.entry.get_text(), start)
			
		dialog.destroy()
		
	def on_preferences(self, widget = None):
		"""显示属性对话框"""
		
		dialog = PreferencesDialog(self)
		
		#还要从 css 中读取属性
		file_object = open(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css")
		try:
			text = file_object.read()
			for i in text.split('}'):
				css = i.split('{')
				if 'GtkWindow' in css[0]:
					Pattern = re.compile(r"background-image: url\('(.*?)'\);")
					match = Pattern.search(css[1])
					if match:
						dialog.set_background_image(match.group(1))
				elif 'GtkNotebook' in css[0]:
					Pattern = re.compile(r"background-color: RGBA\((\d+),(\d+),(\d+),(\d*\.?\d*)\);")
					match = Pattern.search(css[1])
					if match:
						dialog.set_notebook_color(
							string.atoi(match.group(1)),
							string.atoi(match.group(2)),
							string.atoi(match.group(3)),
							string.atof(match.group(4))
						)
				elif 'GtkSourceView' in css[0]:
					Pattern = re.compile(r"font:(.*?) (\d+);")
					match = Pattern.search(css[1])
					if match:
						dialog.set_font(match.group(1),match.group(2))
		finally:
			file_object.close()
				
		response = dialog.run()
		
		file_object = open(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css","w")
		try:
			file_object.write("""GtkWindow {
			background-image: url('""")
			file_object.write(dialog.get_background_image())
			file_object.write("""');
		}
GtkNotebook {
			background-color: RGBA(""")
			file_object.write(dialog.get_notebook_RGBA())
			file_object.write(""");
		}
GtkScrolledWindow , GtkSourceView {
			background-color: RGBA(255,100,100,0);
		}
GtkSourceView:selected { background-color: #C80; }
GtkSourceView { font:""")
			file_object.write(dialog.get_font())
			file_object.write("""; }""")
		finally:
			file_object.close()
		
		dialog.destroy()
		
		#更新样式
		self.set_style()
		
	def on_update_title(self, widget = None):
		"""更新标题栏"""
		cw = self.notebook.get_nth_page(self.notebook.get_current_page())
		cwt = cw.get_child()
		if cwt.change_number == 0:
						
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
		file_object = open(os.environ['HOME']+"/.local/share/bedit/config")
		try:
			file_object.write("width 720\nheight 890")
		finally:
			file_object.close()
	if not os.path.isfile(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css"):
		file_object = open(os.environ['HOME']+"/.local/share/bedit/gtk-widgets3.css")
		try:
			file_object.write("GtkNotebook{background-color:#FFF);}\nGtkScrolledWindow,GtkSourceView{background-color:#000;}\nGtkSourceView:selected{background-color:#C80;}\nGtkSourceView{font:文泉驿等宽微米黑 13;}")
		finally:
			file_object.close()
		
	win = TextViewWindow()
	win.connect("delete-event", win.main_quit)
	#win.show_all()
	Gtk.main()
