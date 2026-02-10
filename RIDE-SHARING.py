import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import heapq
import math
import base64

WIDTH, HEIGHT = 1200, 650 
NODE_RADIUS = 15
AVG_SPEED_KMH = 40

COLOR_BG = "#ecf0f1"
COLOR_SIDEBAR = "#2c3e50"
COLOR_NODE = "#3498db"
COLOR_EDGE = "#bdc3c7"
COLOR_PICKUP = "#2ecc71"
COLOR_DEST = "#e74c3c"
COLOR_PATH = "#f1c40f"
COLOR_TEXT = "#2c3e50"
COLOR_BTN_FIND = "#e67e22"
COLOR_BTN_BOOK = "#27ae60"

CAR_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAALEgAACxIB0t1+/AAAABZ0RVh0Q3JlYXRpb24gVGltZQAxMC8yOS8xMiHZ1r34AAAAB3RJTUUH
3AodFhwl7WFJqgAAAcdJREFUWIXtll2LHEUUhp9Tp6q7Zzc7m2RiDPSGiLgRXwjEhL0RBCF4I4jf
wV/h3+DVeOONIOiN4I2IEDQxbkRMNrub7Znu6a46eTDT2zOzExfcg4dT9fnqPFWn3jNMWZats2d/
S5Zl+V+s/2sBKeX16fT4S0S8bIx501r7wBhz2xjzMyJ+sNb+Mp1OvxoOh98/d3A4HL5rjHkXEd8x
xvwwGo148uQJzjnm8zlEhNFoxHg85uDggN1u981ut/vF/wI4594zxnwbEY+NMfz888988sknfPXV
Vzx69IjdbsdkMmEymTAYDAghcHR0xG63+8o59/1/A0gp34yIn4wxQ2vtY7/fc3R0xGg0IoSAc475
fM58Pmc4HDKbzZJS+uK5g6SU7yLiljHmtjHmmL0/7Pf7Rz/88AOz2Yz5fM5wOGQ2mxFCoN/vc3h4
yG63+zql9M1zB8/fA1LK64h42RjzprX2gTHmtjHm54M/h8Mhs9mM0WhECIF+v08Igd1u94sx5s1/
A/i1LMvX+v3+l9baB8aY28aYn621v0yn06/Ksnz9/wB+LcvylX6//6W19oEx5rYx5mdr7S/T6fSr
siwP/hvAuX7/H+c7/wFlWb72F5+5e9wVnNqRAAAAAElFTkSuQmCC
"""

graph = {
    "Liberty": {"Kalma": 4, "MainMkt": 3, "Gulberg": 5},
    "Kalma": {"Liberty": 4, "Garden": 6, "ModelTown": 7},
    "MainMkt": {"Liberty": 3, "JailRoad": 5},
    "Gulberg": {"Liberty": 5, "JailRoad": 4, "Cantt": 8},
    "Garden": {"Kalma": 6, "Campus": 5},
    "ModelTown": {"Kalma": 7, "Campus": 6, "Township": 5},
    "JailRoad": {"MainMkt": 5, "Gulberg": 4, "Mozang": 6},
    "Cantt": {"Gulberg": 8, "Defence": 7},
    "Campus": {"Garden": 5, "ModelTown": 6, "Thokar": 8},
    "Township": {"ModelTown": 5, "Thokar": 9},
    "Mozang": {"JailRoad": 6, "Mall": 4},
    "Defence": {"Cantt": 7, "Airport": 6},
    "Thokar": {"Campus": 8, "Township": 9, "Motorway": 10},
    "Mall": {"Mozang": 4},
    "Airport": {"Defence": 6},
    "Motorway": {"Thokar": 10}
}

positions = {
    "Liberty": (400, 300), "Kalma": (400, 400), "MainMkt": (300, 250),
    "Gulberg": (500, 250), "Garden": (300, 450), "ModelTown": (450, 500),
    "JailRoad": (400, 150), "Cantt": (650, 250), "Campus": (300, 550),
    "Township": (500, 550), "Mozang": (300, 100), "Defence": (750, 350),
    "Thokar": (200, 500), "Mall": (200, 80), "Airport": (850, 400),
    "Motorway": (100, 550)
}


class RideShareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ride Share System - Earnings & Ratings")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=COLOR_BG)

        self.total_earnings = 0
        self.pickup = None
        self.dest = None
        self.stage = "SELECT_PICKUP"
        self.animation_running = False

        try:
            image_data = base64.b64decode(CAR_BASE64)
            self.car_photo = tk.PhotoImage(data=image_data)
        except Exception as e:
            print(f"Error decoding image: {e}")
            self.car_photo = None 

        self.drivers = [
            {"name": "Ali", "loc": "Airport", "color": "orange", "type": "Mini", "rate": 50},
            {"name": "Bilal", "loc": "Thokar", "color": "purple", "type": "Bike", "rate": 25},
            {"name": "Hamza", "loc": "Mozang", "color": "brown", "type": "Sedan", "rate": 80},
            {"name": "Sara", "loc": "Motorway", "color": "pink", "type": "Mini", "rate": 50},
            {"name": "Zara", "loc": "Cantt", "color": "red", "type": "Lux", "rate": 120}
        ]
        
        self.setup_layout()
        self.draw_graph()
        self.draw_drivers()

    def setup_layout(self):
   
        self.sidebar = tk.Frame(self.root, width=350, bg=COLOR_SIDEBAR)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Ride Booking", bg=COLOR_SIDEBAR, fg="white", font=("Arial", 16, "bold")).pack(pady=(20, 10))

        self.lbl_earnings = tk.Label(self.sidebar, text="Session Earnings: Rs. 0", bg="#34495e", fg="#f1c40f", font=("Arial", 10, "bold"), padx=10, pady=5)
        self.lbl_earnings.pack(fill="x", padx=20, pady=5)

   
        tk.Label(self.sidebar, text="Your Name:", bg=COLOR_SIDEBAR, fg="#bdc3c7").pack(anchor="w", padx=20)
        self.entry_name = tk.Entry(self.sidebar, font=("Arial", 11))
        self.entry_name.pack(fill="x", padx=20, pady=2)

        tk.Label(self.sidebar, text="Pickup:", bg=COLOR_SIDEBAR, fg="#bdc3c7").pack(anchor="w", padx=20)
        self.combo_pickup = ttk.Combobox(self.sidebar, values=list(graph.keys()), state="readonly")
        self.combo_pickup.pack(fill="x", padx=20, pady=2)
        self.combo_pickup.bind("<<ComboboxSelected>>", self.on_pickup_select_ui)

        tk.Label(self.sidebar, text="Destination:", bg=COLOR_SIDEBAR, fg="#bdc3c7").pack(anchor="w", padx=20)
        self.combo_dest = ttk.Combobox(self.sidebar, values=list(graph.keys()), state="readonly")
        self.combo_dest.pack(fill="x", padx=20, pady=2)
        self.combo_dest.bind("<<ComboboxSelected>>", self.on_dest_select_ui)

    
        self.btn_find = tk.Button(self.sidebar, text="FIND DRIVERS", bg=COLOR_BTN_FIND, fg="white", 
                                     font=("Arial", 11, "bold"), relief="flat", command=self.find_drivers)
        self.btn_find.pack(fill="x", padx=20, pady=15)

        columns = ("name", "type", "eta", "fare")
        self.tree = ttk.Treeview(self.sidebar, columns=columns, show="headings", height=6)
        self.tree.heading("name", text="Driver"); self.tree.column("name", width=50)
        self.tree.heading("type", text="Type"); self.tree.column("type", width=40)
        self.tree.heading("eta", text="ETA"); self.tree.column("eta", width=60)
        self.tree.heading("fare", text="Fare"); self.tree.column("fare", width=60)
        self.tree.pack(fill="x", padx=10, pady=5)

        self.btn_book = tk.Button(self.sidebar, text="BOOK SELECTED RIDE", bg=COLOR_BTN_BOOK, fg="white", 
                                     font=("Arial", 11, "bold"), relief="flat", state="disabled", command=self.book_ride)
        self.btn_book.pack(fill="x", padx=20, pady=15)
        
        self.btn_reset = tk.Button(self.sidebar, text="Reset Route", bg="#7f8c8d", fg="white", command=self.reset_system)
        self.btn_reset.pack(side="bottom", fill="x", padx=20, pady=20)

        self.canvas = tk.Canvas(self.root, width=WIDTH-350, height=HEIGHT, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.info_text = self.canvas.create_text(20, 20, anchor="nw", text="Welcome! Select Pickup and Destination.", 
                                                 font=("Arial", 12, "bold"), fill=COLOR_TEXT)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def draw_graph(self):
        self.canvas.delete("edge") 
        self.canvas.delete("node")
        self.canvas.delete("text_dist")
        
        drawn_edges = set()
        for node, neighbors in graph.items():
            x1, y1 = positions[node]
            for neighbor in neighbors:
                edge_key = tuple(sorted((node, neighbor)))
                if edge_key in drawn_edges: continue
                drawn_edges.add(edge_key)

                x2, y2 = positions[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, fill=COLOR_EDGE, width=2, tags="edge")
                
                mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
                self.canvas.create_text(mid_x, mid_y, text=f"{graph[node][neighbor]}km", fill="#7f8c8d", font=("Arial", 8), tags="text_dist")

        self.node_ids = {} 
        for node, (x, y) in positions.items():
            fill_col = COLOR_NODE
            if node == self.pickup: fill_col = COLOR_PICKUP
            elif node == self.dest: fill_col = COLOR_DEST
            
            oid = self.canvas.create_oval(x-NODE_RADIUS, y-NODE_RADIUS, x+NODE_RADIUS, y+NODE_RADIUS, 
                                          fill=fill_col, outline="white", width=2, tags="node")
            self.canvas.create_text(x, y-25, text=node, font=("Arial", 10, "bold"), fill=COLOR_TEXT, tags="node")
            self.node_ids[node] = oid

    def draw_drivers(self):
        self.canvas.delete("driver"); self.canvas.delete("d_label")
        for driver in self.drivers:
            x, y = positions[driver["loc"]]
            if self.car_photo:
                did = self.canvas.create_image(x, y, image=self.car_photo, tags="driver")
            else:
                did = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=driver["color"], tags="driver")
            
            tid = self.canvas.create_text(x, y-20, text=f"{driver['name']}", font=("Arial", 9, "bold"), fill="black", tags="d_label")
            driver["id"] = did
            driver["text_id"] = tid

    def dijkstra(self, start, end):
        pq = [(0, start, [])]
        visited = set()
        while pq:
            cost, node, path = heapq.heappop(pq)
            path = path + [node]
            if node == end: return cost, path
            if node in visited: continue
            visited.add(node)
            for neighbor, weight in graph.get(node, {}).items():
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path))
        return float('inf'), []

    def calculate_time(self, distance):
        return int((distance / AVG_SPEED_KMH) * 60)

    def on_pickup_select_ui(self, event):
        val = self.combo_pickup.get()
        if val: self.update_pickup_selection(val)
    
    def on_dest_select_ui(self, event):
        val = self.combo_dest.get()
        if val: self.update_dest_selection(val)

    def on_canvas_click(self, event):
        if self.animation_running: return
        clicked_node = None
        for node, (nx, ny) in positions.items():
            dist = math.sqrt((event.x - nx)**2 + (event.y - ny)**2)
            if dist <= NODE_RADIUS:
                clicked_node = node
                break
        if not clicked_node: return
        
        if self.stage == "SELECT_PICKUP":
            self.combo_pickup.set(clicked_node)
            self.update_pickup_selection(clicked_node)
        elif self.stage == "SELECT_DEST":
            if clicked_node == self.pickup: return
            self.combo_dest.set(clicked_node)
            self.update_dest_selection(clicked_node)

    def update_pickup_selection(self, node):
        if self.pickup: self.canvas.itemconfig(self.node_ids[self.pickup], fill=COLOR_NODE)
        self.pickup = node
        self.canvas.itemconfig(self.node_ids[self.pickup], fill=COLOR_PICKUP)
        self.stage = "SELECT_DEST"
        self.canvas.itemconfig(self.info_text, text=f"Pickup: {self.pickup}. Select DESTINATION.")

    def update_dest_selection(self, node):
        if node == self.pickup: return
        if self.dest: self.canvas.itemconfig(self.node_ids[self.dest], fill=COLOR_NODE)
        self.dest = node
        self.canvas.itemconfig(self.node_ids[self.dest], fill=COLOR_DEST)
        self.canvas.itemconfig(self.info_text, text=f"Route: {self.pickup}->{self.dest}. Click FIND DRIVERS.")

    def find_drivers(self):
        if not self.pickup or not self.dest:
            messagebox.showerror("Error", "Please select Pickup and Destination first.")
            return

        for item in self.tree.get_children(): self.tree.delete(item)
        self.available_options = []

        trip_dist, self.trip_path = self.dijkstra(self.pickup, self.dest)
        trip_time = self.calculate_time(trip_dist)

        for index, driver in enumerate(self.drivers):
            dist_to_pickup, path_to_pickup = self.dijkstra(driver["loc"], self.pickup)
            eta_mins = self.calculate_time(dist_to_pickup)
    
            fare = int(trip_dist * driver["rate"]) + 50
            
            driver_info = {
                "index": index, 
                "name": driver["name"], 
                "path_to_pickup": path_to_pickup, 
                "trip_time": trip_time,
                "fare": fare
            }
            self.available_options.append(driver_info)
            self.tree.insert("", "end", iid=index, values=(driver["name"], driver["type"], f"{eta_mins} m", f"Rs.{fare}"))

        self.canvas.itemconfig(self.info_text, text=f"Trip: {trip_dist}km. Time: {trip_time} mins.")
        self.btn_book.config(state="normal")
        self.highlight_path(self.trip_path, "#ecf0f1", 1)

    def book_ride(self):
        selected = self.tree.selection()
        if not selected: return
        
        driver_idx = int(selected[0])
        choice = self.available_options[driver_idx]
        actual_driver = self.drivers[driver_idx]
        self.current_fare = choice["fare"] 

        self.stage = "RIDE"
        self.animation_running = True
        self.btn_book.config(state="disabled"); self.btn_find.config(state="disabled")

        self.highlight_path(choice["path_to_pickup"], COLOR_PATH, 4)
        self.animate_car(actual_driver, choice["path_to_pickup"], phase=1, next_path=self.trip_path)

    def highlight_path(self, path, color, width):
        self.canvas.delete("path_line")
        if not path or len(path) < 2: return
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            x1, y1 = positions[u]; x2, y2 = positions[v]
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags="path_line")
            self.canvas.tag_lower("path_line")

    def animate_car(self, driver, path_nodes, phase, next_path=None):
        if len(path_nodes) < 2:
            if phase == 1:
                driver["loc"] = self.pickup
                self.highlight_path(next_path, "#f39c12", 4)
                self.canvas.itemconfig(self.info_text, text="Driver Arrived! Heading to Destination...")
                self.root.after(1000, lambda: self.animate_car(driver, next_path, phase=2))
            elif phase == 2:
                driver["loc"] = self.dest
                self.animation_running = False
                self.canvas.itemconfig(self.info_text, text="Trip Complete!")
                self.finish_ride(driver)
            return
            
        start_pos, end_pos = positions[path_nodes[0]], positions[path_nodes[1]]
        steps = 20
        dx, dy = (end_pos[0]-start_pos[0])/steps, (end_pos[1]-start_pos[1])/steps
        
        def move_step(count):
            if count < steps:
                self.canvas.move(driver["id"], dx, dy)
                self.canvas.move(driver["text_id"], dx, dy)
                self.root.after(20, lambda: move_step(count + 1))
            else:
                self.animate_car(driver, path_nodes[1:], phase, next_path)
        move_step(0)

    def finish_ride(self, driver):
    
        self.total_earnings += self.current_fare
        self.lbl_earnings.config(text=f"Session Earnings: Rs. {self.total_earnings}")

        rating = simpledialog.askinteger("Rate Trip", f"How was your ride with {driver['name']}? (1-5)", minvalue=1, maxvalue=5)
        if rating:
            messagebox.showinfo("Thanks!", f"You rated {driver['name']} {rating} stars.\nRide Cost: Rs. {self.current_fare}")
 
        self.reset_system(soft=True)

    def reset_system(self, soft=False):
        self.canvas.delete("path_line")
        for node, oid in self.node_ids.items(): 
            col = COLOR_NODE
            self.canvas.itemconfig(oid, fill=col)
        
        self.pickup = None; self.dest = None; self.stage = "SELECT_PICKUP"
        self.combo_pickup.set(''); self.combo_dest.set('')
        
        self.btn_book.config(state="disabled"); self.btn_find.config(state="normal")
        
        for item in self.tree.get_children(): self.tree.delete(item)
        
        if not soft:
            self.entry_name.delete(0, tk.END)
            self.total_earnings = 0
            self.lbl_earnings.config(text="Session Earnings: Rs. 0")
            self.draw_drivers()
        
        self.canvas.itemconfig(self.info_text, text="System Ready. Select Pickup.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RideShareApp(root)
    root.mainloop()