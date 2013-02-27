#!/usr/bin/python
#coding:utf8

from gi.repository import Gtk, Pango, GtkSource, Gdk, GObject
import string

def CreateFullMenu(parent = None, history = []):
	"""建立一个菜单栏"""
	mb = Gtk.MenuBar()
	
	mb.append(create_file_menu(parent))
	
	
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
	key, mod = Gtk.accelerator_parse("<Ctrl>X")
	cut.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	cut.set_label("剪切")
	editmenu.append(cut)
	
	copy = Gtk.ImageMenuItem(Gtk.STOCK_COPY)
	key, mod = Gtk.accelerator_parse("<Ctrl>C")
	copy.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	copy.set_label("复制")
	editmenu.append(copy)
	
	paste = Gtk.ImageMenuItem(Gtk.STOCK_PASTE)
	key, mod = Gtk.accelerator_parse("<Ctrl>V")
	paste.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	paste.set_label("粘贴")
	editmenu.append(paste)
	
	editm = Gtk.MenuItem.new_with_label("编辑")
	editm.set_submenu(editmenu)
	mb.append(editm)
	
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
	key, mod = Gtk.accelerator_parse("<Ctrl>N")
	new.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	new.set_label("新建")
	filemenu.append(new)
	new.connect("activate", parent.on_new)
	
	openitem = Gtk.ImageMenuItem(Gtk.STOCK_OPEN)
	key, mod = Gtk.accelerator_parse("<Ctrl>O")
	openitem.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	openitem.set_label("打开")
	filemenu.append(openitem)
	openitem.connect("activate", parent.on_open_file)
	
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	save = Gtk.ImageMenuItem(Gtk.STOCK_SAVE)
	key, mod = Gtk.accelerator_parse("<Ctrl>S")
	save.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	save.set_label("保存")
	filemenu.append(save)
	save.connect("activate", parent.on_save)
	saveAs = Gtk.ImageMenuItem(Gtk.STOCK_SAVE_AS)
	key, mod = Gtk.accelerator_parse("<Shift><Ctrl>S")
	saveAs.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	saveAs.set_label("另存为")
	filemenu.append(saveAs)
	reOpen = Gtk.MenuItem.new_with_label("还原")
	filemenu.append(reOpen)
	
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
		
	print_preview = Gtk.ImageMenuItem(Gtk.STOCK_PRINT_PREVIEW)
	key, mod = Gtk.accelerator_parse("<Shift><Ctrl>P")
	print_preview.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	print_preview.set_label("打印预览")
	filemenu.append(print_preview)
	
	printitem = Gtk.ImageMenuItem(Gtk.STOCK_PRINT)
	key, mod = Gtk.accelerator_parse("<Ctrl>P")
	printitem.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	printitem.set_label("打印")
	filemenu.append(printitem)
	
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	for i in parent.history:
		new = Gtk.MenuItem.new_with_label(i)
		filemenu.append(new)
		new.show()
		new.connect("activate", parent.open_with_menu)
		
	filemenu.append(Gtk.SeparatorMenuItem.new()) #分隔符
	
	close = Gtk.ImageMenuItem(Gtk.STOCK_CLOSE)
	key, mod = Gtk.accelerator_parse("<Ctrl>W")
	close.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	close.set_label("关闭")
	filemenu.append(close)
	
	exit = Gtk.MenuItem.new_with_label("退出")
	key, mod = Gtk.accelerator_parse("<Ctrl>Q")
	exit.add_accelerator("activate", agr, key, mod, Gtk.AccelFlags.VISIBLE)
	filemenu.append(exit)
	
	filem = Gtk.MenuItem.new_with_label("文件")
	filem.set_submenu(filemenu)
	
	return filem
	
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
