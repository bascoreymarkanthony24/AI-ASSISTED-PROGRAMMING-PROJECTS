import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math, json

APP_TITLE = "DPWH RC Box Culvert Preliminary Design & Check (DGCS 2015 Reference)"

class CulvertApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1240x780")
        self.minsize(1080, 680)
        self.vars = {}
        self._style()
        self._build()
        self.update_preview()

    def _style(self):
        s = ttk.Style(self)
        try: s.theme_use('clam')
        except: pass
        s.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        s.configure('H.TLabel', font=('Segoe UI', 10, 'bold'))
        s.configure('Warn.TLabel', font=('Segoe UI', 9, 'bold'))
        s.configure('TButton', padding=6)

    def v(self, name, default):
        x = tk.StringVar(value=str(default)); self.vars[name] = x; return x

    def entry(self, parent, row, label, name, default, unit=""):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', padx=5, pady=3)
        ttk.Entry(parent, textvariable=self.v(name, default), width=12).grid(row=row, column=1, padx=5, pady=3)
        ttk.Label(parent, text=unit).grid(row=row, column=2, sticky='w')

    def _build(self):
        top = ttk.Frame(self); top.pack(fill='x', padx=12, pady=8)
        ttk.Label(top, text=APP_TITLE, style='Title.TLabel').pack(side='left')
        ttk.Label(top, text="Preliminary engineering tool — final design requires engineer/code verification").pack(side='right')

        main = ttk.Panedwindow(self, orient='horizontal'); main.pack(fill='both', expand=True, padx=10, pady=5)
        left = ttk.Frame(main); right = ttk.Frame(main); main.add(left, weight=1); main.add(right, weight=2)

        nb = ttk.Notebook(left); nb.pack(fill='both', expand=True)
        g = ttk.Frame(nb); m = ttk.Frame(nb); soil = ttk.Frame(nb); hyd = ttk.Frame(nb)
        nb.add(g,text='Geometry'); nb.add(m,text='Materials / Loads'); nb.add(soil,text='Soil'); nb.add(hyd,text='Hydraulics')

        self.entry(g,0,'No. of cells','cells',2,'')
        self.entry(g,1,'Clear span / cell','span',3.0,'m')
        self.entry(g,2,'Clear height','height',3.0,'m')
        self.entry(g,3,'Top slab thickness','ttop',0.35,'m')
        self.entry(g,4,'Bottom slab thickness','tbot',0.40,'m')
        self.entry(g,5,'Exterior wall thickness','twext',0.35,'m')
        self.entry(g,6,'Interior wall thickness','twint',0.30,'m')
        self.entry(g,7,'Fill above top slab','fill',1.50,'m')
        self.entry(g,8,'Culvert length','length',12.0,'m')

        self.entry(m,0,"Concrete f'c",'fc',27.6,'MPa')
        self.entry(m,1,'Rebar fy (main)','fy',415,'MPa')
        self.entry(m,2,'Concrete unit weight','gc',24.0,'kN/m³')
        self.entry(m,3,'Pavement + wearing load','pave',5.0,'kPa')
        self.entry(m,4,'Live-load surcharge (editable)','lls',12.0,'kPa')
        self.entry(m,5,'Strength dead-load factor','fd',1.25,'')
        self.entry(m,6,'Strength earth-load factor','fe',1.35,'')
        self.entry(m,7,'Strength surcharge factor','fl',1.75,'')

        self.entry(soil,0,'Soil unit weight','gs',19.0,'kN/m³')
        self.entry(soil,1,'Friction angle φ','phi',30.0,'deg')
        self.entry(soil,2,'Allowable bearing','qallow',96.0,'kPa')
        self.entry(soil,3,'Groundwater depth from grade','gwd',5.0,'m')

        self.entry(hyd,0,'Design discharge Q','Q',8.0,'m³/s')
        self.entry(hyd,1,"Manning's n",'n',0.015,'')
        self.entry(hyd,2,'Culvert bed slope','slope',0.005,'m/m')
        self.entry(hyd,3,'Design return period','rp',25,'yr')
        self.entry(hyd,4,'Check return period','rpc',50,'yr')

        btn = ttk.Frame(left); btn.pack(fill='x', pady=8)
        ttk.Button(btn,text='ANALYZE / CHECK',command=self.analyze).pack(side='left',padx=3)
        ttk.Button(btn,text='Save Inputs',command=self.save_inputs).pack(side='left',padx=3)
        ttk.Button(btn,text='Load Inputs',command=self.load_inputs).pack(side='left',padx=3)
        ttk.Button(btn,text='Export Report',command=self.export_report).pack(side='left',padx=3)

        self.tabs = ttk.Notebook(right); self.tabs.pack(fill='both', expand=True)
        pv = ttk.Frame(self.tabs); rs = ttk.Frame(self.tabs); notes = ttk.Frame(self.tabs)
        self.tabs.add(pv,text='Section Preview'); self.tabs.add(rs,text='Calculation Summary'); self.tabs.add(notes,text='DGCS / Design Notes')
        self.status = ttk.Label(rs, text='DESIGN STATUS: NOT YET CHECKED', font=('Segoe UI', 14, 'bold'), anchor='center')
        self.status.pack(fill='x', padx=8, pady=8)
        self.canvas = tk.Canvas(pv, bg='white'); self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Configure>', lambda e:self.update_preview())
        self.result = tk.Text(rs, wrap='word', font=('Consolas',10)); self.result.pack(fill='both',expand=True)
        note_text = (
            "IMPLEMENTATION BASIS / LIMITATIONS\n\n"
            "• References: DPWH DGCS 2015 Vol. 4 (Highway Design) and Vol. 5 (Bridge Design), plus project-specific DPWH standard drawings/specifications.\n"
            "• Standard RCBC drawings located in DPWH project documents indicate applicability for fill heights 0–3.0 m; above this requires special design.\n"
            "• Hydrologic/hydraulic, scour, settlement and geotechnical analyses remain required.\n"
            "• Typical cited standard-plan values include f'c = 27.6 MPa and assumed allowable bearing = 96 kPa, which must be verified against project requirements/geotechnical data.\n"
            "• National-road culvert hydrology reference: 25-year design flood with 50-year check/freeboard.\n"
            "• DGCS references minimum culvert velocity about 0.8 m/s and maximum about 5 m/s.\n\n"
            "IMPORTANT: Live-load distribution, dynamic load allowance, LRFD load combinations, resistance factors, crack control, fatigue where applicable, and detailed RC member capacities must be checked against the controlling DGCS/AASHTO provisions before construction use. Factors in this prototype are editable intentionally.\n"
        )
        t=tk.Text(notes,wrap='word'); t.insert('1.0',note_text); t.config(state='disabled'); t.pack(fill='both',expand=True)

        for var in self.vars.values(): var.trace_add('write', lambda *_: self.update_preview())

    def num(self,k): return float(self.vars[k].get())

    def update_preview(self):
        if not hasattr(self,'canvas'): return
        c=self.canvas; c.delete('all'); W=max(c.winfo_width(),700); H=max(c.winfo_height(),500)
        try:
            n=max(1,int(float(self.vars['cells'].get()))); b=self.num('span'); h=self.num('height');
            tt=self.num('ttop'); tb=self.num('tbot'); te=self.num('twext'); ti=self.num('twint'); fill=self.num('fill')
        except: return
        total_w=n*b+2*te+(n-1)*ti; total_h=h+tt+tb+fill
        scale=min((W-120)/max(total_w,1),(H-130)/max(total_h,1)); x0=60; ybase=H-60
        def rect(x1,y1,x2,y2,fillc='#d9dde3'):
            c.create_rectangle(x1,y1,x2,y2,fill=fillc,outline='#25364a',width=2)
        # soil fill
        top_y=ybase-(h+tt+tb+fill)*scale
        slabtop_y=ybase-(h+tt+tb)*scale
        c.create_rectangle(x0,top_y,x0+total_w*scale,slabtop_y,fill='#ead9b5',outline='')
        # slabs
        rect(x0,slabtop_y,x0+total_w*scale,slabtop_y+tt*scale)
        rect(x0,ybase-tb*scale,x0+total_w*scale,ybase)
        # walls
        walltop=slabtop_y+tt*scale; wallbot=ybase-tb*scale
        rect(x0,walltop,x0+te*scale,wallbot); x=x0+te*scale
        for i in range(n-1):
            x += b*scale; rect(x,walltop,x+ti*scale,wallbot); x += ti*scale
        rect(x0+(total_w-te)*scale,walltop,x0+total_w*scale,wallbot)
        c.create_text(W/2,25,text=f'{n}-Cell Reinforced Concrete Box Culvert',font=('Segoe UI',14,'bold'))
        c.create_text(W/2,47,text=f'Clear opening: {b:.2f} m × {h:.2f} m per cell | Fill = {fill:.2f} m',font=('Segoe UI',10))
        c.create_text(x0+total_w*scale/2, top_y+max(fill*scale/2,12), text='EARTH FILL',font=('Segoe UI',9,'bold'))

    def analyze(self):
        try:
            n=int(self.num('cells')); b=self.num('span'); h=self.num('height'); tt=self.num('ttop'); tb=self.num('tbot'); te=self.num('twext'); ti=self.num('twint'); fill=self.num('fill')
            gc=self.num('gc'); gs=self.num('gs'); pave=self.num('pave'); lls=self.num('lls'); phi=self.num('phi'); qallow=self.num('qallow')
            fd=self.num('fd'); fe=self.num('fe'); fl=self.num('fl'); Q=self.num('Q'); man=self.num('n'); S=self.num('slope'); L=self.num('length')
            if min(n,b,h,tt,tb,te,gc,gs,qallow,man,S,L)<=0: raise ValueError('Inputs must be positive.')
        except Exception as e:
            messagebox.showerror('Input error',str(e)); return

        total_w=n*b+2*te+(n-1)*ti
        Ka=math.tan(math.radians(45-phi/2))**2
        q_fill=gs*fill
        q_top_dead=gc*tt+q_fill+pave
        q_top_service=q_top_dead+lls
        q_top_strength=fd*(gc*tt+pave)+fe*q_fill+fl*lls
        p_lat_top=Ka*(gs*fill+lls)
        p_lat_bot=Ka*(gs*(fill+h)+lls)

        # Preliminary one-way fixed-end strip demand indicators; NOT final frame analysis.
        Mu_top=q_top_strength*b*b/12.0
        Vu_top=q_top_strength*b/2.0
        Mwall=(p_lat_bot-p_lat_top)*h*h/20.0 + p_lat_top*h*h/12.0

        # rough concrete volume per metre culvert length and total
        area_conc=total_w*(tt+tb)+2*te*h+(n-1)*ti*h
        vol=area_conc*L
        # crude service bearing indicator using structure + fill + top surcharge, per m length
        Wconc=area_conc*gc
        Wfill=total_w*fill*gs
        qbase=(Wconc+Wfill+total_w*(pave+lls))/total_w

        # full-flow Manning capacity (rectangular opening total)
        A=n*b*h; P=n*(b+2*h); R=A/P
        v=(1/man)*(R**(2/3))*math.sqrt(S); Qcap=A*v

        warnings=[]
        failed_checks=[]
        passed_checks=[]
        if fill>3.0: warnings.append('Fill > 3.0 m: outside cited DPWH standard RCBC drawing applicability; SPECIAL DESIGN required.')
        if self.num('fc')<27.6: warnings.append("Concrete f'c is below 27.6 MPa standard-plan value found in cited DPWH RCBC drawing.")
        if qbase>qallow:
            warnings.append('Preliminary service bearing indicator exceeds entered allowable bearing pressure.')
            failed_checks.append(f'Bearing pressure: {qbase:.2f} kPa > {qallow:.2f} kPa')
        else:
            passed_checks.append(f'Bearing pressure: {qbase:.2f} kPa <= {qallow:.2f} kPa')
        if v<0.8:
            warnings.append('Full-flow velocity is below 0.8 m/s DGCS reference minimum; sedimentation/self-cleaning review required.')
            failed_checks.append(f'Hydraulic velocity: {v:.2f} m/s < 0.80 m/s')
        if v>5.0:
            warnings.append('Full-flow velocity exceeds 5 m/s DGCS reference maximum; erosion/scour protection review required.')
            failed_checks.append(f'Hydraulic velocity: {v:.2f} m/s > 5.00 m/s')
        if 0.8 <= v <= 5.0:
            passed_checks.append(f'Hydraulic velocity: 0.80 <= {v:.2f} <= 5.00 m/s')
        if Qcap<Q:
            warnings.append('Approximate full-flow Manning capacity is below entered design discharge.')
            failed_checks.append(f'Hydraulic capacity: {Qcap:.2f} m³/s < Q = {Q:.2f} m³/s')
        else:
            passed_checks.append(f'Hydraulic capacity: {Qcap:.2f} m³/s >= Q = {Q:.2f} m³/s')

        if fill > 3.0:
            failed_checks.append(f'Standard-plan fill applicability: {fill:.2f} m > 3.00 m')
        else:
            passed_checks.append(f'Standard-plan fill applicability: {fill:.2f} m <= 3.00 m')

        # Overall status is deliberately a SCREENING status until complete LRFD structural
        # analysis and RC member capacities are implemented.
        if failed_checks:
            status_text = 'PRELIMINARY SCREENING: FAILED / REQUIRES REDESIGN OR REVIEW'
        else:
            status_text = 'PRELIMINARY SCREENING: PASSED — STRUCTURAL LRFD CHECK STILL REQUIRED'

        lines=[]
        lines += ['DPWH RC BOX CULVERT — PRELIMINARY CALCULATION SUMMARY','='*68,'',status_text,'-'*68,'']
        lines += ['CHECK-BY-CHECK STATUS']
        lines += [('PASS  | '+x) for x in passed_checks]
        lines += [('FAIL  | '+x) for x in failed_checks]
        lines += ['', 'IMPORTANT: This status does NOT yet certify structural adequacy. A final PASS requires the complete DGCS 2015 / controlling AASHTO LRFD rigid-frame analysis and reinforced-concrete strength/service checks.', '']
        lines += [f'Cells                         : {n}',f'Clear opening / cell          : {b:.3f} m × {h:.3f} m',f'Total structural width        : {total_w:.3f} m',f'Fill height                   : {fill:.3f} m','']
        lines += ['LOAD INDICATORS',f'Fill pressure on top           : {q_fill:10.3f} kPa',f'Top service vertical pressure : {q_top_service:10.3f} kPa',f'Top factored pressure         : {q_top_strength:10.3f} kPa',f'Active earth coefficient Ka   : {Ka:10.4f}',f'Lateral pressure at wall top  : {p_lat_top:10.3f} kPa',f'Lateral pressure at wall base : {p_lat_bot:10.3f} kPa','']
        lines += ['PRELIMINARY STRUCTURAL DEMAND INDICATORS',f'Top slab Mu indicator         : {Mu_top:10.3f} kN·m/m',f'Top slab Vu indicator         : {Vu_top:10.3f} kN/m',f'Exterior wall M indicator     : {Mwall:10.3f} kN·m/m','NOTE: These are screening values, not a substitute for the final rigid-frame LRFD analysis.','']
        lines += ['FOUNDATION / QUANTITY INDICATORS',f'Concrete section area         : {area_conc:10.3f} m² per m length',f'Approx. concrete volume       : {vol:10.3f} m³',f'Prelim. service base pressure : {qbase:10.3f} kPa',f'Entered allowable bearing     : {qallow:10.3f} kPa','']
        lines += ['HYDRAULIC SCREENING (FULL-FLOW MANNING)',f'Flow area                     : {A:10.3f} m²',f'Hydraulic radius              : {R:10.3f} m',f'Full-flow velocity            : {v:10.3f} m/s',f'Approx. full-flow capacity    : {Qcap:10.3f} m³/s',f'Entered design discharge      : {Q:10.3f} m³/s','']
        lines += ['WARNINGS / REQUIRED ENGINEERING REVIEW']
        lines += [('• '+w) for w in warnings] if warnings else ['• No screening warning triggered by the entered parameters.']
        lines += ['', 'FINAL DESIGN ITEMS NOT YET AUTOMATED IN THIS PROTOTYPE:',
                  '• Exact AASHTO/DPWH vehicular live-load distribution through fill and dynamic allowance',
                  '• 2D rigid-frame stiffness analysis for all governing load cases/combinations',
                  '• LRFD flexure, shear, axial-flexure, minimum steel, spacing and crack-control checks',
                  '• Uplift/flotation and groundwater load cases',
                  '• Differential settlement, scour and foundation/geotechnical design',
                  '• Inlet/outlet control hydraulic analysis and headwater/freeboard checks',
                  '• Wingwall/headwall/apron design and seismic checks where applicable']
        self.report='\n'.join(lines); self.result.delete('1.0','end'); self.result.insert('1.0',self.report); self.status.config(text='DESIGN STATUS: ' + status_text); self.tabs.select(1)

    def save_inputs(self):
        p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')])
        if p:
            with open(p,'w') as f: json.dump({k:v.get() for k,v in self.vars.items()},f,indent=2)

    def load_inputs(self):
        p=filedialog.askopenfilename(filetypes=[('JSON','*.json')])
        if p:
            with open(p) as f: d=json.load(f)
            for k,val in d.items():
                if k in self.vars: self.vars[k].set(val)
            self.update_preview()

    def export_report(self):
        if not hasattr(self,'report'): self.analyze()
        if not hasattr(self,'report'): return
        p=filedialog.asksaveasfilename(defaultextension='.txt',filetypes=[('Text report','*.txt')])
        if p:
            with open(p,'w',encoding='utf-8') as f: f.write(self.report)
            messagebox.showinfo('Export','Report saved.')

if __name__=='__main__':
    CulvertApp().mainloop()
