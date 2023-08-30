from tkinter import *
from tkinter import ttk

class Terminal():
    def __init__(self,prompt=False):
        self.root = Tk()
        self.root.title("NodeNetwork-Terminal")
        self.root.geometry("720x700+50+50")
        self.max_height=12000
        
        s = ttk.Style()
        s.configure('new.TFrame', background='black')

        self.commands = []
        self.ent = []
        self.index = 0
        self.y = 0
        self.base_route_text = "NodeNetwok://route$"
        self.route_text = "NodeNetwok://route$"
        self.prompt=prompt
        
        self.tBody = ttk.Frame(self.root)     
        self.cbody = Canvas(self.tBody,bg="black",height=self.max_height)
        self.sbar = ttk.Scrollbar(self.tBody, orient="vertical", command=self.cbody.yview)
        self.body = ttk.Frame(self.cbody,style="new.TFrame")
        self.body.configure(height=1200)
        self.body.bind(
            "<Configure>",
            lambda e: self.cbody.configure(
                scrollregion=self.cbody.bbox("all")
                )
            )
        self.cbody.create_window((0, 0), window=self.body, anchor="nw")
        self.cbody.configure(yscrollcommand=self.sbar.set)
        self.sbar.pack(side="right",fill='y') 

        self.tBody.pack(expand=True,fill=BOTH)
        self.cbody.pack(side=LEFT,expand=True,fill=BOTH)
        #self.create_base()
        #self.root.mainloop()

    def exec(self,text):
        self.ent[self.index].config(state= "disabled",disabledbackground="black",disabledforeground="#1DB700")
        self.commands.append(self.ent[self.index].get())
        print(self.ent[self.index].get())
        lbl = Label(self.body,text="",bg="black",font=("Monaco",13),fg='#39FF14',anchor='w',width=10)
        lbl.grid(row=self.y+1,column=0)
        text = "you command has \nbenn executed\n hdefkjkjkdgjkfljgklfdjgkljdfkgjdklfgjkdjgldjhkldfjhkldjhldfjhkldfjhfdklhjkldftgfklfgljkjhdkljhdkljhkldjhkljdj"
        lbl = Label(self.body,wraplength=400,text=text,bg="black",font=("Monaco",13),fg='#39FF14',anchor='w',width=100)
        lbl.grid(row=self.y+1,column=1)
        
        self.index+=1
        self.y+=2
        return self.Next()
        
        #self.create_base()

    def Prompt(self,text):
        pass

    def Next(self):
        return self.create_base()

    def create_base(self):
        lbl = Label(self.body,text=self.route_text,bg="black",font=("Monaco",14),fg="white")
        lbl.grid(row=self.y,column=0)
        ent = Entry(self.body,bg="black",fg='#39FF14',width=100,bd=0,font=("Monaco",14))
        ent.config(insertbackground="green")
        ent.bind("<Return>",self.exec)
        ent.grid(row=self.y,column=1)
        self.ent.append(ent)
        ent.focus_set()
        
    #def 
    def loop(self):
        self.create_base()
        self.root.mainloop()
        
        
t=Terminal()
t.loop()

