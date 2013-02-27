#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject, GdkPixbuf
import string
  	
class PreferencesDialog(Gtk.Dialog):
	"""属性对话框"""
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "bedit 首选项", parent, 
			Gtk.DialogFlags.MODAL, buttons=(
				Gtk.STOCK_HELP, Gtk.ResponseType.HELP,
				Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
			)
		)
		
		box = self.get_content_area()
		
		self.notebook = Gtk.Notebook()
		
		self.notebook.append_page(Gtk.Box(spacing=6), Gtk.Label("查看"))
		self.notebook.append_page(Gtk.Box(spacing=6), Gtk.Label("编辑器"))
		
		#字体和颜色
		boxFontColor = Gtk.Box(spacing=6)
		frameColorBackground = Gtk.Frame()
		frameColorBackground.set_label("配色和背景")
		boxFontColor.add(frameColorBackground)
		self.notebook.append_page(boxFontColor, Gtk.Label("字体和颜色"))
		self.fsBackground = Gtk.FileChooserButton()
		self.gridColor = Gtk.Grid()
		frameColorBackground.add(self.gridColor)
		self.gridColor.attach(self.fsBackground,1,0,1,1)
		#文件选择按钮也可以有消息映射的
		self.fsBackground.connect("file-set", self.background_selected)
		self.gridColor.attach(Gtk.Label("背景图片："),0,0,1,1)
		
		self.thumbnail = Gtk.Image()
		self.gridColor.attach(self.thumbnail,0,1,2,1)
		
		self.thumbnailLabel = Gtk.Label("宽度： 高度：")
		self.gridColor.attach(self.thumbnailLabel,0,2,2,1)
		
		self.gridColor.attach(Gtk.Label("标签页颜色："),0,3,1,1)
		self.buttonNotebookColor = Gtk.ColorButton()
		self.buttonNotebookColor.set_use_alpha(True)
		self.gridColor.attach(self.buttonNotebookColor,1,3,1,1)
		
		#插件
		self.notebook.append_page(Gtk.Box(spacing=6), Gtk.Label("插件"))
		
		#历史记录
		self.history = parent.history
		modelHistory = Gtk.ListStore(str)
		self.treeViewHistory = Gtk.TreeView(modelHistory)
		cell = Gtk.CellRendererText()
		treeviewcolumn = Gtk.TreeViewColumn("路径", cell, text=0)
		self.treeViewHistory.append_column(treeviewcolumn)
		for i in parent.history:
			modelHistory.append([i])
		gridHistory = Gtk.Grid()
		gridHistory.attach(self.treeViewHistory,0,0,2,1)
		clearOne = Gtk.Button("移除历史记录")
		clearAll = Gtk.Button("移除全部历史记录")
		clearOne.connect("clicked", self.on_clear_one)
		gridHistory.attach(clearOne,0,1,1,1)
		gridHistory.attach(clearAll,1,1,1,1)
		self.notebook.append_page(gridHistory, Gtk.Label("历史记录"))
		box.add(self.notebook)
		
		self.show_all()
		
	def on_clear_one(self, widget = None):
		"""从列表中删除一个历史记录"""
		path, column = self.treeViewHistory.get_cursor()
		#self.treeViewHistory.remove_column(column)
		del self.history[string.atoi(path.to_string())]
		
	def set_background_image(self, url):
		self.fsBackground.set_filename(url)
		
		imgp = GdkPixbuf.Pixbuf.new_from_file(url)
		width  = imgp.get_width()
		height = imgp.get_height()
		scale = min(320.0/float(width),400/float(height))
		n_width = width*scale
		n_height = height*scale
		self.thumbnail.set_from_pixbuf(imgp.scale_simple(n_width,n_height,GdkPixbuf.InterpType.BILINEAR))
		
		self.thumbnailLabel.set_label("宽度："+str(width)+" 高度："+str(height))
		self.show_all()
		
	def set_notebook_color(self, r,g,b,a):
		self.buttonNotebookColor.set_color(Gdk.Color(r*256,g*256,b*256))
		self.buttonNotebookColor.set_alpha(a*65535)
		
	def background_selected(self, widget):
		self.set_background_image(widget.get_filename())
		
	def get_background_image(self):
		"""获得背景图片的路径"""
		return self.fsBackground.get_filename()
		
	def get_notebook_RGBA(self):
		"""返回标签的颜色"""
		rgb = self.buttonNotebookColor.get_color()
		return str(rgb.red/256)+","+str(rgb.green/256)+","+str(rgb.blue/256)+","+str(self.buttonNotebookColor.get_alpha()/65535.0)
