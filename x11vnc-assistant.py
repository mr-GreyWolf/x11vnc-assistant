#!/usr/bin/python
# -*- coding: utf-8 -*-
# Для работы требуется установить пакет python-wx : apt install python-wxgtk3.0
import wx, socket, os, subprocess, random, getpass, gettext

basePath = os.path.dirname(__file__)
#basePath = '.'
gettext.install('x11vnc-assistant', basePath+'/locale', unicode=True)

trayTooltip_text = _('Connect to session (x11vnc-assistant)')
windowTitle_text = _('Preferences of x11vnc-assistant')
windowHeader_text = _('Information for connect to session:')
separator = ', ' # Разделитель для показа параметров
menuInfo_text = _('Information')
menuExit_text = _('Quit x11vnc-assistant')
hostName_text = _('Server')
portNumber_text = _('Port')
passwdFull_text = _('Full Password')
passwdView_text = _('View Password')
params_text = _('Parameters list:')
buttonClose_text = _('Close')
trayIcon = basePath + '/icons/x11vnc24.png'
windowIcon = basePath + '/icons/x11vnc24.png'
passwdFull = (''.join([random.choice(list('1234567890')) for x in range(5)]))
passwdRead = (''.join([random.choice(list('1234567890')) for x in range(3)]))
filePasswd = '/tmp/.x11vnc-' + getpass.getuser() + '-passwd'
fileFlag = '/tmp/.x11vnc-' + getpass.getuser()
tag = 'x11vnc-' + getpass.getuser()
hostName = socket.getfqdn()
portNumber = ''	 # Номер порта x11vnc

# Запуск только одного экземпляра скрипта
cmd = ['pgrep -f ' + os.path.basename(__file__)]
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
my_pid, err = process.communicate()
l=len(my_pid.splitlines())
if l >= 3: exit()

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
	self.frame = frame
	super(TaskBarIcon, self).__init__()
	self.set_icon(trayIcon)
	self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
	menu = wx.Menu()
	create_menu_item(menu, menuInfo_text, self.info)
	menu.AppendSeparator()
	create_menu_item(menu, menuExit_text, self.on_exit)
	return menu

    def set_icon(self, path):
	icon = wx.IconFromBitmap(wx.Bitmap(path))
	self.SetIcon(icon, trayTooltip_text)

    def on_left_down(self, event):	# Нажатие на иконку в системной области
	SingleInstanceFrame()

    def info(self, event):	# пункт меню Информация
        SingleInstanceFrame()

    def on_exit(self, event):	# пункт меню Выход
	wx.CallAfter(self.Destroy)
	SingleInstanceFrame().Close()
	x11vnc_close()
	self.frame.Close()

class App(wx.App):
    def OnInit(self):
	frame=wx.Frame(None)
	self.SetTopWindow(frame)
	TaskBarIcon(frame)
	return True

class MyPanel(wx.Panel):
    def __init__(self, parent):
	wx.Panel.__init__(self, parent)
	self.Centre()

class SingleInstanceFrame(wx.Frame):
    instance = None
    init = 0
    def __new__(self, *args, **kwargs):

	if self.instance is None:
	    self.instance = wx.Frame.__new__(self)
	elif not self.instance:
	    self.instance = wx.Frame.__new__(self)
	elif self.instance: # Окно уже открыть, нужно его закрыть и открыть заново, чтобы переключить контекст на него
	    self.instance.Close()
	    self.instance = wx.Frame.__new__(self)
	return self.instance

    def onClose(self, event):
        self.Close()

    def __init__(self):
	if self.init:
	    return
	self.init = 1
	wx.Frame.__init__(self, None, title = windowTitle_text, style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
	panel = MyPanel(self)

	self.SetIcon(wx.Icon(windowIcon))
	sizer = wx.GridBagSizer(15, 15)

	sizer.Add(wx.StaticText(panel, label = windowHeader_text), pos=(0, 0), span=(1,3), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)

	#icon = wx.StaticBitmap(panel, bitmap=wx.Bitmap(windowIcon))
	#sizer.Add(icon, pos=(0, 4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)

	sizer.Add(wx.StaticLine(panel), pos=(1, 0), span=(1, 6), flag=wx.EXPAND|wx.BOTTOM, border=5)
	
	sizer.Add(wx.StaticText(panel, label = hostName_text), pos=(2, 0), span=(1,1), flag=wx.LEFT, border=10)
	sizer.Add(wx.TextCtrl(panel, value = hostName, style = wx.TE_READONLY), pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND)

	sizer.Add(wx.StaticText(panel, label = portNumber_text), pos=(3, 0), span=(1,1), flag=wx.LEFT, border=10)
	sizer.Add(wx.TextCtrl(panel, value = portNumber, style = wx.TE_READONLY), pos=(3, 1), span=(1, 3), flag=wx.TOP)

	sizer.Add(wx.StaticText(panel, label = passwdFull_text), pos=(4, 0), span=(1,1), flag=wx.LEFT|wx.TOP, border=10)
	sizer.Add(wx.TextCtrl(panel, value = passwdFull, style = wx.TE_READONLY), pos=(4, 1), span=(1, 3), flag=wx.TOP, border=5)

	sizer.Add(wx.StaticText(panel, label = passwdView_text), pos=(5, 0), span=(1,1), flag=wx.LEFT|wx.TOP, border=10)
	sizer.Add(wx.TextCtrl(panel,value = passwdRead, style = wx.TE_READONLY), pos=(5, 1), span=(1, 3), flag=wx.TOP, border=5)

	sizer.Add(wx.StaticLine(panel), pos=(6, 0), span=(1, 6), flag=wx.EXPAND|wx.BOTTOM, border=5)
	# Список параметров
	FIELD_PARM_TEXT = hostName + separator + portNumber + separator + passwdFull + separator + passwdRead
	sizer.Add(wx.StaticText(panel, label = params_text), pos=(7, 0), span=(1,1), flag=wx.LEFT|wx.TOP, border=5)
	sizer.Add(wx.TextCtrl(panel, value = FIELD_PARM_TEXT, style = wx.TE_MULTILINE|wx.TE_READONLY), pos=(8, 0), span=(1, 6), flag=wx.TOP|wx.EXPAND, border=5)

	buttonClose = wx.Button(panel, label = buttonClose_text)
	buttonClose.Bind(wx.EVT_BUTTON, self.onClose)
	sizer.Add(buttonClose, pos=(9, 2), span=(1, 1), flag=wx.BOTTOM, border=10)

	panel.SetSizer(sizer)
	sizer.Fit(self)
	self.Show()

def main():
    app = App(False)
    SingleInstanceFrame()
    app.MainLoop()

def x11vnc_passwd():	# Сохраняем пароли
    passwd_file = open(filePasswd, 'w')
    passwd_file.write(passwdFull + '\n')
    passwd_file.write('__BEGIN_VIEWONLY__\n')
    passwd_file.write(passwdRead + '\n')
    passwd_file.close()
    os.chmod(filePasswd, 0600)

def x11vnc_start():	# Запускаем сервер
    os.system('x11vnc -q -forever -shared -autoport 5901 -bg -passwdfile ' + filePasswd + ' -flag ' + fileFlag + ' -tag ' + tag + '-nomodtweak -capslock')   
    flag_file = open(fileFlag, 'r')
    portNumber = (flag_file.read().replace('PORT=','')).replace('\n','')
    flag_file.close()
    return portNumber

def x11vnc_close():	# Завершаем сервер
    proc = subprocess.Popen(["pkill", "-f", tag], stdout=subprocess.PIPE)
    proc.wait()
    if os.path.exists(filePasswd): os.remove (filePasswd)
    if os.path.exists(fileFlag): os.remove (fileFlag)

if __name__ == '__main__':
    x11vnc_close()
    x11vnc_passwd()
    portNumber=x11vnc_start()
    main()
