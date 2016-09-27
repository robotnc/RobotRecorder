#-*-coding:utf-8-*-
#Automatic recorder for Speech data collection
#robot.ling@nationalchip.com
from Tkinter import *
import tkMessageBox
import tkFont
import time
import recorder
import os

SCRIPT_DIR = './script'
OUT_DIR = './data'

def message(msg,title="Message"):
   tkMessageBox.showinfo(title, msg)

class Script():
  """
  script file should be *.txt, and the format shoud be:
	1 xxxxxx
	2 xxxxxx
	...
	N ScriptText
  """
  def __init__(self,script_dir):
	self.script_dir = script_dir
	self.script_dict = {}
	self.length = 0

  def read_file(self,script_file):
	self.script_dict = {}
	with open(os.path.join(self.script_dir,script_file),'r') as f:
		lines = f.readlines()
		for x in lines:
			new_dict={x.split(' ')[0] : x.split(' ')[1].strip()}
			self.script_dict.update(new_dict)
	self.length = len(self.script_dict)

  def get_list(self):
	self.script_list = []
	for files in os.listdir(self.script_dir):
		if files.split('.')[-1].strip()=='txt':
			self.script_list.append(files.strip())
	print "Script_list:",self.script_list
	return self.script_list

  def get_text(self,text_id):
	return self.script_dict[str(text_id)]


class Recorder_ui():
  def __init__(self,out_dir):
	self.mode = 'REC'
	self.is_recording = False
	self.out_dir = out_dir
	self.t = 0
	self.start = time.time()

	self.Rec_script = Script(SCRIPT_DIR)
	script_list = self.Rec_script.get_list()
	self.script_id = 0

	self.root = root = Tk()
  	root.wm_title("Robot Auto Recoder V0.0")
	root.geometry("800x600")
	ft_big = tkFont.Font(size=20)
	#define frames
	frame_top = Frame(root,width = 800, height= 50, bg="#ffffff")
	frame_mid = Frame(root,width = 800, height= 50, bg="red")
	frame_can = Frame(root,width = 800, height= 50, bg="blue")
	frame_bot = Frame(root,width = 800, height= 50, bg="grey")
	frame_top.grid(row=0,column=0,sticky=W,pady=10)
	frame_mid.grid(row=1,column=0,sticky=W,pady=2)
	frame_can.grid(row=2,column=0,sticky=W,pady=0,padx=0)
	frame_bot.grid(row=3,column=0,sticky=W,pady=2)
	#Frame top: Configuration area
  	Label(frame_top,text="输入姓名(英文)").grid(row=0,column=0,sticky=W,padx=2)
  	Label(frame_top,text="选择录音脚本",).grid(row=0,column=2,sticky=E,padx=2)
  	self.name_entry = Entry(frame_top,text='robot')
	self.cur_script = cur_script=StringVar()
	cur_script.set("------")
	#self.script_entry = apply(OptionMenu,(frame_top,cur_script) + tuple(script_list))
	self.script_entry = OptionMenu(frame_top,cur_script,*script_list)
	self.name_entry.grid(row=0,column=1,sticky=W,padx=2)
	self.script_entry.grid(row=0,column=3,sticky=W,padx=2)
	self.cur_script.trace('w',self.update_script)
	#SID
	self.sid = StringVar()
	self.sid.set(str(self.script_id)+'/'+str(self.Rec_script.length))
	Label(frame_top,textvariable=self.sid).grid(row=0,column=5,sticky=E)
	#Frame mid: Display current recording text
	self.rec_text = rec_text = StringVar()
	rec_text.set("欢迎参与录音，填写姓名选择录音脚本后，点击按钮开始录音！")
  	Label(frame_mid,textvariable=rec_text,bg="yellow",width=60,height=5,font=ft_big
		).grid(sticky=W,ipadx=0)
	#Frame can: draw canvas for time line
	self.rec_time=rec_time=DoubleVar()
	#Progressbar(frame_can,variable=rec_time,maximum=10.0).grid()
  	self.can = can = Canvas(frame_can,background="grey",width=780,height=50,borderwidth=0)
	can.grid()
	#Frame bot: add buttons for control
  	self.b1 = b1 = Button(frame_bot,text="上一个",background="grey",height=5,font=ft_big,width=30)
	b1.grid(row=0,column=0,sticky=W+E+N+S,pady=5)
  	self.b2 = b2 = Button(frame_bot,text="录音模式，点击暂停",background="grey",height=5,font=ft_big,width=30)
	b2.grid(row=0,column=1,sticky=W+E+N+S,pady=5)
  	self.b3 = b3 = Button(frame_bot,text="开始录音",background="red",height=5,font=ft_big,width=60)
	b3.grid(row =1,sticky=W+E,columnspan=5)
	#Bind functions for buttons
  	b1.bind('<Button-1>',self.previous)
  	b2.bind('<Button-1>',self.pause)
  	b3.bind('<Button-1>',self.next)

	#create recorder
  	self.rec = recorder.Recorder(
			channels=1,rate=16000,frames_per_buffer=1024)
	self.update_time()
	#mainloop
  	root.mainloop()

  def pause(self,event):
	if self.mode == 'PAUSE':
		self.b2["text"] = "录音模式，点击暂停"
		self.mode = 'REC'
		self.b2["fg"]="black"
	else:
		self.stop_rec()
		self.mode = 'PAUSE'
		self.b2["text"] = "已暂停，点击恢复"
		self.b2["fg"]="red"

  def next(self,event):
	if self.name_entry.get()=='' or self.script_entry=='------':
		message("请输入录音者姓名并选择录音脚本！")
		return
	if self.script_id < self.Rec_script.length:
		self.script_id += 1
		self.b3["text"]="下一个"
	else:
		self.stop_rec()
		message("录音结束!")
		self.update_script('')
		return
		
	self.rec_text.set(self.Rec_script.get_text(self.script_id))
	self.sid.set(str(self.script_id)+'/'+str(self.Rec_script.length))
	if self.mode == 'REC':
	  if self.is_recording == True:
		self.stop_rec()
	  self.start_rec()

  def previous(self,event):
	if self.name_entry.get()=='' or self.script_entry=='------':
		message("Please input speaker name and selct scripts!")
		return
	if self.script_id > 1:
		 self.script_id -= 1
	else:
		message("已经返回第一条!")
		return
		
	self.rec_text.set(self.Rec_script.get_text(self.script_id))
	self.sid.set(str(self.script_id)+'/'+str(self.Rec_script.length))
	if self.mode == 'REC':
	  if self.is_recording == True:
		self.stop_rec()
	  self.start_rec()

  def start_rec(self):
	rec_time = time.strftime('%Y%m%d',time.localtime(time.time()))
	filename = self.name_entry.get()+"_"+self.cur_script.get().split('.')[0]
	filename +="_"+rec_time+"_"+str(self.script_id)+".wav"
	filename = os.path.join(self.out_dir,filename)
	print "start rec:",filename
	self.rec_file = self.rec.open(filename,'wb')
	self.rec_file.start_recording()
	self.is_recording = True
	self.t = 0
	with open(filename+'.lab','w') as f:
		label = ''.join(self.rec_text.get().split(','))
		print label
		f.write(label.encode('utf-8'))

  def stop_rec(self):
	print "Stop rec"
	self.can.create_rectangle((0,0),(800,100),fill="grey")
	if self.is_recording:
		time.sleep(0.1)
		self.rec_file.stop_recording()
		self.is_recording = False
		#self.update_time(mode='stop')
	else:
		print "Noting to stop"

  def update_time(self,mode=None):
	if self.is_recording:
		self.t += 4 
		self.can.create_rectangle((0,0),(self.t,100),fill="blue")
	else:
		self.can.create_rectangle((0,0),(800,100),fill="grey")
	self.root.after(50,self.update_time)

  def update_script(self,*args):
	script_file = self.cur_script.get()
	print "get script file:",script_file
	self.rec_text.set("Loading...")
	self.script = self.Rec_script.read_file(script_file)
	self.script_id = 0
	self.rec_text.set(self.Rec_script.get_text(1))
	self.sid.set('1/'+str(self.Rec_script.length))
	self.b3["text"]="开始录音"
	
if __name__ == "__main__":
  out_dir = OUT_DIR
  if not os.path.exists(out_dir):
	os.makedirs(out_dir)
  rec_ui = Recorder_ui(out_dir)
