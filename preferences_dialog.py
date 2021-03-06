#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject, GdkPixbuf
import string
import re
		
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
		
		self.checkLineNumber = Gtk.CheckButton("显示行号")
		gridView = Gtk.Grid()
		gridView.attach(self.checkLineNumber,0,0,1,1)
		self.notebook.append_page(gridView, Gtk.Label("查看"))
		
		self.create_frameEditor()
		
		self.create_frameFontColor()
		
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
		gridHistory.attach(Gtk.Label("历史记录保存条目"),0,2,1,1)
		self.historySpin = Gtk.SpinButton()
		self.historySpin.set_increments(1,1)
		self.historySpin.set_range(0,99)
		gridHistory.attach(self.historySpin,1,2,1,1)
		self.notebook.append_page(gridHistory, Gtk.Label("历史记录"))
		box.add(self.notebook)
		
		#工具栏
		self.create_frameToolbar()
		
		self.show_all()
		
	def create_frameEditor(self):
		#编辑器
		boxEditor = Gtk.Grid()
		
		boxEditor.attach(Gtk.Label("制表符宽度："), 0,0,1,1)
		self.tabWidth = Gtk.SpinButton()
		self.tabWidth.set_increments(1,1)
		self.tabWidth.set_range(0,16)
		boxEditor.attach(self.tabWidth,3,0,2,1)
		
		self.checkAutoSave = Gtk.CheckButton("自动保存间隔")
		boxEditor.attach(self.checkAutoSave,0,1,1,1)
				
		self.notebook.append_page(boxEditor, Gtk.Label("编辑器"))
		
	def create_frameFontColor(self):
		#字体和颜色
		boxFontColor = Gtk.Grid()
		
		#字体框架
		frameFont = Gtk.Frame()
		frameFont.set_label("字体")
		boxFontColor.attach(frameFont,0,0,1,1)
		self.fsFont = Gtk.FontButton()
		frameFontHBox = Gtk.Grid()
		frameFontHBox.attach(Gtk.Label("编辑器字体："),0,0,1,1)
		frameFontHBox.attach(self.fsFont,1,0,1,1)
		frameFontHBox.attach(Gtk.Label("编辑器字体颜色："),0,1,1,1)
		self.buttonFontColor = Gtk.ColorButton()
		frameFontHBox.attach(self.buttonFontColor,1,1,1,1)
		frameFont.add(frameFontHBox)
		
		frameColorBackground = Gtk.Frame()
		frameColorBackground.set_label("背景")
		boxFontColor.attach(frameColorBackground,0,1,1,1)
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
		
	
	def create_frameToolbar(self):
		"""和工具栏相关"""
		boxToolbar = Gtk.Grid()
		self.notebook.append_page(boxToolbar, Gtk.Label("工具栏"))
		
		boxToolbar.attach(Gtk.Label("按钮间距"),0,0,2,1)
		self.toolbarPadding = Gtk.SpinButton()
		self.toolbarPadding.set_increments(1,1)
		self.toolbarPadding.set_range(0,10)
		boxToolbar.attach(self.toolbarPadding,3,0,2,1)

		
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
		
	def set_font(self, name, size):
		self.fsFont.set_font_name(name+" "+size)
		
	def set_font_color(self, r, g, b):
		self.buttonFontColor.set_color(Gdk.Color(r*256,g*256,b*256))
		
	def set_historyListRange(self, size):
		self.historySpin.set_value(size)
		
	def background_selected(self, widget):
		self.set_background_image(widget.get_filename())
		
	def get_background_image(self):
		"""获得背景图片的路径"""
		return self.fsBackground.get_filename()
		
	def get_notebook_RGBA(self):
		"""返回标签的颜色"""
		rgb = self.buttonNotebookColor.get_color()
		return str(rgb.red/256)+","+str(rgb.green/256)+","+str(rgb.blue/256)+","+str(self.buttonNotebookColor.get_alpha()/65535.0)
		
	def get_font(self):
		return self.fsFont.get_font_name()
		
	def get_historyListRange(self):
		return self.historySpin.get_value_as_int()
		
	def get_tabWidth(self):
		return self.tabWidth.get_value_as_int()
		
	def set_tabWidth(self, value):
		self.toolbarPadding.set_value(value)
		
	def set_css(self, text):
		"""使用 css 进行设置"""
		for i in text.split('}'):
			css = i.split('{')
			if 'GtkWindow' in css[0]:
				Pattern = re.compile(r"background-image: url\('(.*?)'\);")
				match = Pattern.search(css[1])
				if match:
					self.set_background_image(match.group(1))
			elif 'GtkNotebook' in css[0] :
				Pattern = re.compile(r"background-color: RGBA\((\d+),(\d+),(\d+),(\d*\.?\d*)\);")
				match = Pattern.search(css[1])
				if match:
					self.set_notebook_color(
						string.atoi(match.group(1)),
						string.atoi(match.group(2)),
						string.atoi(match.group(3)),
						string.atof(match.group(4))
					)
			elif 'GtkSourceView' in css[0]:
				Pattern = re.compile(r"font:(.*?) (\d+);")
				match = Pattern.search(css[1])
				if match:
					self.set_font(match.group(1),match.group(2))
				Pattern = re.compile(r"color: RGB\((\d+),(\d+),(\d+)\);")
				match = Pattern.search(css[1])
				if match:
					self.set_font_color(
							string.atoi(match.group(1)),
							string.atoi(match.group(2)),
							string.atoi(match.group(3)))
			elif 'GtkButton' in css[0]:
				Pattern = re.compile(r"padding: (\d+)px;")
				match = Pattern.search(css[1])
				if match:
					self.toolbarPadding.set_value(string.atoi(match.group(1)))
							
	def get_css(self):
		text = "GtkWindow {\n"
		text += "	background-image: url('"
		text +=	self.get_background_image()
		text +=	"""');
		}
GtkScrolledWindow , GtkSourceView , GtkGrid tab:nth-child(first) {
			background-color: RGBA(255,100,100,0);
		}
GtkNotebook {
			background-color: RGBA("""
		text +=	self.get_notebook_RGBA()
		text +=	""");
		}
GtkSourceView:selected { background-color: #C80; }
GtkSourceView { font:"""
		text +=	self.get_font()
		text +=	""";
			color: #000; }\n"""
		text += "tab:nth-child(first) GtkButton {\n"
		text += "	padding: "+str(self.toolbarPadding.get_value_as_int())+"px;\n"
		text += "}"
		return text
		
	def get_line_number(self):
		return self.checkLineNumber.get_active()
		
	def set_line_number(self, value):
		self.checkLineNumber.set_active(value)
		
	def getAutoSave(self):
		return self.checkAutoSave.get_active()
		
	def setAutoSave(self, value):
		self.checkAutoSave.set_active(value)
