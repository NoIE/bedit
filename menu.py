#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject
import string

def CreateFullMenu(parent = None, history = []):
	"""建立一个菜单栏"""
	mb = Gtk.MenuBar()
	
	mb.append(create_file_menu(parent))
	
	
	mb.append(create_edit_menu(parent))
	
	mb.append(create_view_menu(parent))
		
	mb.append(create_search_menu(parent))
	
	return mb
	
def create_file_menu(parent):

	#文件菜单
	filemenu = Gtk.Menu()
	
	agr = Gtk.AccelGroup()
	filemenu.set_accel_group(agr)
	parent.add_accel_group(agr)
	
	new = Gtk.ImageMenuItem(Gtk.STOCK_NEW)
	new.set_use_stock(True)
	new.set_always_show_image(True)
	key, mod = Gtk.accelerator_parse("<Ctrl>N")
	new.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	new.set_label("新建")
	filemenu.append(new)
	new.connect("activate", parent.on_new)
	
	item = create_item_with_icon(Gtk.STOCK_OPEN, "<Ctrl>O", "打开", agr)
	item.connect("activate", parent.on_open_file)
	filemenu.append(item)
	
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	item = create_item_with_icon(Gtk.STOCK_SAVE, "<Ctrl>S", "保存", agr)
	item.connect("activate", parent.on_save)
	filemenu.append(item)
	
	item = create_item_with_icon(Gtk.STOCK_SAVE_AS, "<Shift><Ctrl>S", "另存为", agr)
	item.connect("activate", parent.on_save_as)
	filemenu.append(item)
	
	item = create_item_with_icon(Gtk.STOCK_REVERT_TO_SAVED, "", "还原", agr)
	item.connect("activate", parent.on_revert_to_saved)
	filemenu.append(item)
		
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
		
	item = create_item_with_icon(Gtk.STOCK_PRINT_PREVIEW, "<Shift><Ctrl>P", agr = agr)
	filemenu.append(item)
		
	item = create_item_with_icon(Gtk.STOCK_PRINT, "<Ctrl>P", agr = agr)
	filemenu.append(item)
		
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	for i in parent.history:
		new = create_item_with_icon(Gtk.STOCK_FILE, "", agr = agr)
		new = Gtk.MenuItem.new_with_label(i)
		filemenu.append(new)
		new.show()
		new.connect("activate", parent.open_with_menu)
		
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	item = create_item_with_icon(Gtk.STOCK_CLOSE, "<Ctrl>W", agr = agr)
	item.connect("activate", parent.on_close)
	filemenu.append(item)
	
	item = create_item_with_icon(Gtk.STOCK_QUIT, "<Ctrl>Q", agr = agr)
	filemenu.append(item)
	
	filem = create_item_with_icon(Gtk.STOCK_FILE, "", agr = agr)
	filem.set_submenu(filemenu)
	
	return filem
	
def create_edit_menu(parent):

	#编辑菜单
	editmenu = Gtk.Menu()
	
	agr = Gtk.AccelGroup()
	editmenu.set_accel_group(agr)
	parent.add_accel_group(agr)
	
	undo = Gtk.ImageMenuItem(Gtk.STOCK_UNDO)
	key, mod = Gtk.accelerator_parse("<Ctrl>Z")
	undo.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	undo.set_label("撤销")
	editmenu.append(undo)
	
	redo = Gtk.ImageMenuItem(Gtk.STOCK_REDO)
	key, mod = Gtk.accelerator_parse("<Shift><Ctrl>Z")
	redo.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	redo.set_label("重做")
	editmenu.append(redo)
	
	editmenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	cut = Gtk.ImageMenuItem(Gtk.STOCK_CUT)
	#key, mod = Gtk.accelerator_parse("<Ctrl>X")
	#cut.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	cut.set_label("剪切")
	editmenu.append(cut)
	
	copy = Gtk.ImageMenuItem(Gtk.STOCK_COPY)
	#key, mod = Gtk.accelerator_parse("<Ctrl>C")
	#copy.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	copy.set_label("复制")
	editmenu.append(copy)
	
	paste = Gtk.ImageMenuItem(Gtk.STOCK_PASTE)
	#key, mod = Gtk.accelerator_parse("<Ctrl>V")
	#paste.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	paste.set_label("粘贴")
	editmenu.append(paste)
	
	item = Gtk.ImageMenuItem(Gtk.STOCK_DELETE)
	item.set_label("删除")
	editmenu.append(item)
	
	editmenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	item = Gtk.ImageMenuItem(Gtk.STOCK_SELECT_ALL)
	item.set_label("全选")
	editmenu.append(item)
	
	
	editm = Gtk.MenuItem.new_with_label("编辑")
	editm.set_submenu(editmenu)
	
	return editm
	
def create_view_menu(parent):
	
	#查看菜单
	viewmenu = Gtk.Menu()
	
	wrap = Gtk.MenuItem.new_with_label("自动换行")
	viewmenu.append(wrap)
	
	viewm = Gtk.MenuItem.new_with_label("查看")
	viewm.set_submenu(viewmenu)
	
	#语法加亮菜单
	languagemenu = Gtk.Menu()
	languagem = Gtk.MenuItem.new_with_label("语法高亮模式")
	languagem.set_submenu(languagemenu)
	
	textm = Gtk.MenuItem.new_with_label("纯文本")
	languagemenu.append(textm)
	
	#标记
	markmenu = Gtk.Menu()
	markm = Gtk.MenuItem.new_with_label("标记")
	markm.set_submenu(markmenu)
	languagemenu.append(markm)
	
	BibTeXm = Gtk.MenuItem.new_with_label("BibTeX")
	markmenu.append(BibTeXm)
	
	Docbookm = Gtk.MenuItem.new_with_label("Docbook")
	markmenu.append(Docbookm)
	
	DTDm = Gtk.MenuItem.new_with_label("DTD")
	markmenu.append(DTDm)
	
	gtkdocm = Gtk.MenuItem.new_with_label("gtk-doc")
	markmenu.append(gtkdocm)
	
	Haddockm = Gtk.MenuItem.new_with_label("Haddock")
	markmenu.append(Haddockm)
	
	HTMLm = Gtk.MenuItem.new_with_label("html")
	HTMLm.connect("activate", parent.set_language)
	markmenu.append(HTMLm)
	
	XMLm = Gtk.MenuItem.new_with_label("xml")
	XMLm.connect("activate", parent.set_language)
	markmenu.append(XMLm)
	
	#脚本
	scriptmenu = Gtk.Menu()
	scriptm = Gtk.MenuItem.new_with_label("脚本")
	scriptm.set_submenu(scriptmenu)
	languagemenu.append(scriptm)
	
	Luam = Gtk.MenuItem.new_with_label("Lua")
	scriptmenu.append(Luam)
	
	Pythonm = Gtk.MenuItem.new_with_label("Python")
	scriptmenu.append(Pythonm)
	
	#源代码
	sourcemenu = Gtk.Menu()
	sourcem = Gtk.MenuItem.new_with_label("源代码")
	sourcem.set_submenu(sourcemenu)
	languagemenu.append(sourcem)
	
	c = Gtk.MenuItem.new_with_label("c")
	c.connect("activate", parent.set_language)
	sourcemenu.append(c)
	
	cpp = Gtk.MenuItem.new_with_label("cpp")
	cpp.connect("activate", parent.set_language)
	sourcemenu.append(cpp)
	
	sql = Gtk.MenuItem.new_with_label("sql")
	sql.connect("activate", parent.set_language)
	sourcemenu.append(sql)
	
	viewmenu.append(languagem)
	
	return viewm
	
	
def create_search_menu(parent):
	
	searchmenu = Gtk.Menu()
	
	find = Gtk.ImageMenuItem(Gtk.STOCK_FIND)
	find.set_label("查找")
	searchmenu.append(find)
	
	searchm = Gtk.MenuItem.new_with_label("搜索")
	searchm.set_submenu(searchmenu)
	
	return searchm
	
def create_item_with_icon(icon, accel, label = None, agr = None):
	"""建立一个菜单项"""
	new = Gtk.ImageMenuItem(icon)
	new.set_use_stock(True)
	new.set_always_show_image(True)
	if accel != "" and accel != None:
		key, mod = Gtk.accelerator_parse(accel)
		new.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	if label != None:
		new.set_label(label)
	return new
