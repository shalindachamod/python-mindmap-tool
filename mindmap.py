import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, colorchooser, filedialog, messagebox
import random
import json
from PIL import Image, ImageDraw, ImageFont

class MindMapApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Python Mind Map Tool - Infinite Panning Edition")
        self.geometry("1250x780")
        
        # Appearance Mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # App State Storage
        self.nodes = {}
        self.connections = []  
        self.zoom_level = 1.0  
        self.is_locked = False  
        
        self.selected_node = None
        self.connecting_source_node = None  
        self.current_project_name = "Untitled Mind Map"

        # 1. Control Panel
        self.control_panel = ctk.CTkFrame(self, height=60)
        self.control_panel.pack(fill="x", side="top", padx=10, pady=5)

        # Buttons
        self.add_btn = ctk.CTkButton(self.control_panel, text="+ Add Node", font=("Segoe UI", 12, "bold"), width=90, command=self.add_node)
        self.add_btn.pack(side="left", padx=3, pady=10)
        
        self.zoom_in_btn = ctk.CTkButton(self.control_panel, text="🔍 In", font=("Segoe UI", 12), width=50, fg_color="#28a745", hover_color="#218838", command=self.zoom_in)
        self.zoom_in_btn.pack(side="left", padx=3, pady=10)

        self.zoom_out_btn = ctk.CTkButton(self.control_panel, text="🔍 Out", font=("Segoe UI", 12), width=50, fg_color="#dc3545", hover_color="#c82333", command=self.zoom_out)
        self.zoom_out_btn.pack(side="left", padx=3, pady=10)
        
        # Storage Buttons
        self.save_btn = ctk.CTkButton(self.control_panel, text="💾 Save Project", font=("Segoe UI", 12, "bold"), width=110, fg_color="#ffc107", text_color="#212529", hover_color="#e0a800", command=self.save_project)
        self.save_btn.pack(side="left", padx=5, pady=10)

        self.open_btn = ctk.CTkButton(self.control_panel, text="📂 Open Project", font=("Segoe UI", 12, "bold"), width=110, fg_color="#17a2b8", hover_color="#138496", command=self.open_project)
        self.open_btn.pack(side="left", padx=5, pady=10)
        
        # Lock Switch
        self.lock_switch = ctk.CTkSwitch(self.control_panel, text="🔒 Lock Map", font=("Segoe UI", 12, "bold"), command=self.toggle_lock)
        self.lock_switch.pack(side="left", padx=15, pady=10)

        # Export Buttons
        self.png_btn = ctk.CTkButton(self.control_panel, text="📸 PNG", font=("Segoe UI", 12), width=70, fg_color="#4e4e5a", command=self.export_png)
        self.png_btn.pack(side="left", padx=3, pady=10)

        self.pdf_btn = ctk.CTkButton(self.control_panel, text="📄 PDF", font=("Segoe UI", 12), width=70, fg_color="#6f42c1", hover_color="#5a34a1", command=self.export_pdf)
        self.pdf_btn.pack(side="left", padx=3, pady=10)
        
        # Project Name Label
        self.project_label = ctk.CTkLabel(self.control_panel, text=f"Project: {self.current_project_name}", font=("Segoe UI", 12, "italic"), text_color="#a1a1aa")
        self.project_label.pack(side="right", padx=15, pady=10)

        # 2. Workspace Canvas
        self.canvas = tk.Canvas(self, bg="#1e1e24", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=5)

        # 🌐 NEW CANVAS BINDINGS FOR PANNING:
        self.canvas.bind("<Button-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.drag_pan)

        # 3. Create Default Root Node
        self.create_node_element(600, 375, "Main Topic", is_root=True)

    # 🌐 NEW PANNING LOGIC
    def start_pan(self, event):
      
        clicked_item = self.canvas.find_withtag("current")
        if not clicked_item:
            
            self.canvas.config(cursor="fleur")
            self.canvas.scan_mark(event.x, event.y)
            self.is_panning = True
        else:
            self.is_panning = False

    def drag_pan(self, event):
        
        if hasattr(self, 'is_panning') and self.is_panning:
            self.canvas.scan_dragto(event.x, event.y, gain=1)
           
            self.canvas.bind("<ButtonRelease-1>", lambda e: self.canvas.config(cursor=""))

    def create_node_element(self, x, y, text, is_root=False, custom_id=None, color=None, bg_color=None):
        node_id = custom_id if custom_id else f"node_{random.randint(1000, 9999)}"
        
        default_bg = "#007bff" if is_root else "#2d2d38"
        default_outline = "#0056b3" if is_root else "#3b82f6"
        
        actual_bg = bg_color if bg_color else default_bg
        actual_outline = color if color else default_outline
        
        tag = f"tag_{node_id}"
        
        r_x, r_y = 70 * self.zoom_level, 35 * self.zoom_level
        shape = self.canvas.create_oval(x-r_x, y-r_y, x+r_x, y+r_y, fill=actual_bg, outline=actual_outline, width=2, tags=(tag, "node_shape"))
        label = self.canvas.create_text(x, y, text=text, fill="#ffffff", font=("Segoe UI", int(11 * self.zoom_level), "bold" if is_root else "normal"), tags=(tag, "node_text"), width=int(120 * self.zoom_level), justify="center")

        self.nodes[node_id] = {
            "shape": shape,
            "label": label,
            "tag": tag,
            "x": x,
            "y": y,
            "text": text,
            "is_root": is_root,
            "color": actual_outline,
            "bg_color": actual_bg
        }

        # Event Bindings for Individual Nodes 
        self.canvas.tag_bind(tag, "<Button-1>", lambda event, nid=node_id: self.on_node_click(event, nid))
        self.canvas.tag_bind(tag, "<B1-Motion>", lambda event, nid=node_id: self.on_node_drag(event, nid))
        self.canvas.tag_bind(tag, "<Button-3>", lambda event, nid=node_id: self.show_context_menu(event, nid))

    def add_node(self):
        if self.is_locked:
            messagebox.showwarning("Locked", "Mind Map It is currently locked! Unlock it before changing it.")
            return
        
       
        cx = self.canvas.canvasx(600)
        cy = self.canvas.canvasy(375)
        x = cx + random.randint(-150, 150)
        y = cy + random.randint(-150, 150)
        self.create_node_element(x, y, "New Idea")

    def toggle_lock(self):
        self.is_locked = self.lock_switch.get() == 1

    def on_node_click(self, event, node_id):
        if self.is_locked: return
        self.selected_node = node_id
       
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_node_drag(self, event, node_id):
        if self.is_locked or self.selected_node != node_id: return
        
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        dx = cur_x - self.start_x
        dy = cur_y - self.start_y
        
        self.canvas.move(self.nodes[node_id]["tag"], dx, dy)
        self.nodes[node_id]["x"] += dx
        self.nodes[node_id]["y"] += dy
        
        self.start_x = cur_x
        self.start_y = cur_y
        self.update_lines()

    def show_context_menu(self, event, node_id):
        if self.is_locked:
            messagebox.showinfo("Locked", "Mind Map It is currently locked so changes cannot be made.")
            return
            
        menu = tk.Menu(self, tearoff=0, bg="#2a2a35", fg="#ffffff", activebackground="#007bff", font=("Segoe UI", 11))
        menu.add_command(label="📝 Edit Text", command=lambda: self.edit_node_text(node_id))
        menu.add_command(label="🎨 Change Color", command=lambda: self.change_node_color(node_id))
        
        if self.connecting_source_node is None:
            menu.add_command(label="🔗 Connect to Link", command=lambda: self.start_line_connection(node_id))
        else:
            menu.add_command(label="🎯 Complete Link Here", command=lambda: self.end_line_connection(node_id))
            
        if not self.nodes[node_id]["is_root"]:
            menu.add_separator()
            menu.add_command(label="🗑️ Delete Node", command=lambda: self.delete_node(node_id))
            
        menu.tk_popup(event.x_root, event.y_root)

    def edit_node_text(self, node_id):
        current_text = self.nodes[node_id]["text"]
        new_text = simpledialog.askstring("Edit Node", "Enter new text:", initialvalue=current_text, parent=self)
        if new_text and new_text.strip() != "":
            self.nodes[node_id]["text"] = new_text.strip()
            self.canvas.itemconfig(self.nodes[node_id]["label"], text=new_text.strip())

    def start_line_connection(self, node_id):
        self.connecting_source_node = node_id
        self.canvas.itemconfig(self.nodes[node_id]["shape"], outline="#28a745", width=3)

    def end_line_connection(self, node_id):
        source = self.connecting_source_node
        target = node_id
        if source != target:
            x1, y1 = self.nodes[source]["x"], self.nodes[source]["y"]
            x2, y2 = self.nodes[target]["x"], self.nodes[target]["y"]
            line_color = self.nodes[source]["color"]
            line = self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=2)
            self.canvas.tag_lower(line) 
            self.connections.append({"line_id": line, "source_id": source, "target_id": target})
        self.canvas.itemconfig(self.nodes[source]["shape"], outline=self.nodes[source]["color"], width=2)
        self.connecting_source_node = None

    def change_node_color(self, node_id):
        color_code = colorchooser.askcolor(title="Choose Node Color", parent=self)[1]
        if color_code:
            self.nodes[node_id]["color"] = color_code
            if self.nodes[node_id]["is_root"]:
                self.nodes[node_id]["bg_color"] = color_code
                self.canvas.itemconfig(self.nodes[node_id]["shape"], fill=color_code, outline=color_code)
            else:
                self.canvas.itemconfig(self.nodes[node_id]["shape"], outline=color_code)
            for conn in self.connections:
                if conn["source_id"] == node_id:
                    self.canvas.itemconfig(conn["line_id"], fill=color_code)

    def delete_node(self, node_id):
        self.canvas.delete(self.nodes[node_id]["tag"])
        remaining_connections = []
        for conn in self.connections:
            if conn["source_id"] == node_id or conn["target_id"] == node_id:
                self.canvas.delete(conn["line_id"])
            else:
                remaining_connections.append(conn)
        self.connections = remaining_connections
        del self.nodes[node_id]

    def zoom_in(self):
        scale_factor = 1.1
        self.zoom_level *= scale_factor
        cx = self.canvas.canvasx(600)
        cy = self.canvas.canvasy(375)
        self.canvas.scale("all", cx, cy, scale_factor, scale_factor)
        self.update_internal_coordinates(cx, cy, scale_factor)

    def zoom_out(self):
        scale_factor = 0.9
        self.zoom_level *= scale_factor
        cx = self.canvas.canvasx(600)
        cy = self.canvas.canvasy(375)
        self.canvas.scale("all", cx, cy, scale_factor, scale_factor)
        self.update_internal_coordinates(cx, cy, scale_factor)

    def update_internal_coordinates(self, cx, cy, factor):
        for node_id in self.nodes:
            self.nodes[node_id]["x"] = cx + (self.nodes[node_id]["x"] - cx) * factor
            self.nodes[node_id]["y"] = cy + (self.nodes[node_id]["y"] - cy) * factor

    def update_lines(self):
        for conn in self.connections:
            s_id = conn["source_id"]
            t_id = conn["target_id"]
            x1, y1 = self.nodes[s_id]["x"], self.nodes[s_id]["y"]
            x2, y2 = self.nodes[t_id]["x"], self.nodes[t_id]["y"]
            self.canvas.coords(conn["line_id"], x1, y1, x2, y2)

    def save_project(self):
        name_input = simpledialog.askstring("Project Name", "Enter Mind Map Name:", initialvalue=self.current_project_name, parent=self)
        if not name_input or name_input.strip() == "": return
        
        self.current_project_name = name_input.strip()
        self.project_label.configure(text=f"Project: {self.current_project_name}")

        nodes_data = {}
        for nid, n in self.nodes.items():
            nodes_data[nid] = {
                "x": n["x"], "y": n["y"], "text": n["text"],
                "is_root": n["is_root"], "color": n["color"], "bg_color": n["bg_color"]
            }

        connections_data = []
        for conn in self.connections:
            connections_data.append({
                "source_id": conn["source_id"], "target_id": conn["target_id"]
            })

        full_project_data = {
            "project_name": self.current_project_name,
            "zoom_level": self.zoom_level,
            "nodes": nodes_data,
            "connections": connections_data
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Mind Map Project", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(full_project_data, f, indent=4)
            messagebox.showinfo("Saved", f'"{self.current_project_name}"  Saved successfully!')

    def open_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("Mind Map Project", "*.json")])
        if not file_path: return

        with open(file_path, "r") as f:
            data = json.load(f)

        self.canvas.delete("all")
        self.nodes.clear()
        self.connections.clear()

        self.current_project_name = data.get("project_name", "Untitled Mind Map")
        self.zoom_level = data.get("zoom_level", 1.0)
        self.project_label.configure(text=f"Project: {self.current_project_name}")

        for nid, n in data["nodes"].items():
            self.create_node_element(n["x"], n["y"], n["text"], is_root=n["is_root"], custom_id=nid, color=n["color"], bg_color=n["bg_color"])

        for conn in data["connections"]:
            s_id = conn["source_id"]
            t_id = conn["target_id"]
            line_color = self.nodes[s_id]["color"]
            line = self.canvas.create_line(self.nodes[s_id]["x"], self.nodes[s_id]["y"], self.nodes[t_id]["x"], self.nodes[t_id]["y"], fill=line_color, width=2)
            self.canvas.tag_lower(line)
            self.connections.append({"line_id": line, "source_id": s_id, "target_id": t_id})

        self.is_locked = False
        self.lock_switch.deselect()
        messagebox.showinfo("Loaded", f'"{self.current_project_name}" Opened successfully! ')

    def generate_pillow_image(self):
        
        width = max(self.canvas.winfo_width(), 1200)
        height = max(self.canvas.winfo_height(), 800)
        img = Image.new("RGB", (width, height), "#1e1e24")
        draw = ImageDraw.Draw(img)
        for conn in self.connections:
            s = self.nodes[conn["source_id"]]
            t = self.nodes[conn["target_id"]]
            draw.line([(s["x"], s["y"]), (t["x"], t["y"])], fill=s["color"], width=2)
        for node_id, node in self.nodes.items():
            x, y = node["x"], node["y"]
            r_x, r_y = 70 * self.zoom_level, 35 * self.zoom_level
            draw.ellipse([x - r_x, y - r_y, x + r_x, y + r_y], fill=node["bg_color"], outline=node["color"], width=2)
            draw.text((x, y), node["text"], fill="#ffffff", anchor="mm", align="center")
        return img

    def export_png(self):
        img = self.generate_pillow_image()
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file_path: img.save(file_path); messagebox.showinfo("Success", "PNG Saved!")

    def export_pdf(self):
        img = self.generate_pillow_image()
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Document", "*.pdf")])
        if file_path: pdf_img = img.convert("RGB"); pdf_img.save(file_path, "PDF", resolution=100.0); messagebox.showinfo("Success", "PDF Saved!")

if __name__ == "__main__":
    app = MindMapApp()
    app.mainloop()
