import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import math
from tkinter import filedialog
import numpy as np

#################################################
# Other
AUTHOR = 'Itsame Mario, Itsame Luigi'
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0


#################################################


class WindForceGUI(tk.Tk):
    """
    Create GUI
    """

    # static class variables
    MAIN_WIDTH = 900
    MAIN_HEIGHT = 600
    CANVAS_MAIN_WIDTH = 300
    CANVAS_MAIN_HEIGHT = 330
    STANDARD_FONT_1 = ('Arial', 12)
    STANDARD_FONT_2 = ('Arial', 8)
    STANDARD_FONT_BUTTON = ('Arial', 10)

    def __init__(self):
        """
        Constructor, inherits from tkinter
        """
        super().__init__()
        self.init_main_window()
        self.solution = None
        self.input_parameters_init = {'sections': None,
                                 'springs': {'base_cx': 0,
                                             'base_cy': 0,
                                             'base_phix': 0,
                                             'base_phiy': 0,
                                             'head_cx': 0},
                                 'masses': {'base_m': 0,
                                            'head_m': 0},
                                 'forces': {'f_excite': 0,
                                            'f_head': 0,
                                            'm_head': 0,
                                            'f_rotor': 0,
                                            'qu_impulse': 0,
                                            'qo_impulse': 0,
                                            'nbr_periods': 0,
                                            'delta_t': 0,
                                            'num_1': 0,
                                            'num_2': 0},
                                 'excentricity': {'exc_ex': 0,
                                                  'exc_EA': 0,
                                                  'exc_EIy': 0,
                                                  'exc_EIz': 0,
                                                  'exc_GIt': 0,
                                                  'exc_mass': 0,
                                                  'exc_area': 0,
                                                  'exc_Ip': 0},
                                 'calculation_param': {'fem_density': 0,
                                                       'fem_nbr_eigen_freq': 0,
                                                       'fem_dmas': 0,
                                                       'fem_exc': 0}}
        self.input_parameters = self.input_parameters_init

    def init_main_window(self):
        """
        Crates Main Window
        """

        # root window is self to distinguish instance variables from root window
        root = self

        # Title, Geometry and fonts
        root.title('WINDFORCE')
        root.geometry(f"{WindForceGUI.MAIN_WIDTH}x{WindForceGUI.MAIN_HEIGHT}")
        root.resizable(False, False)
        standard_font_1_bold = tkFont.Font(family="Arial", size=12, weight='bold')

        # Add system image
        system_image_label = tk.Label(root, text="System Definition:", font=standard_font_1_bold)
        system_image_label.place(relx=0.6, rely=0.05)
        try:
            system_image = Image.open(r'supp\system.png')
            root.system_image_tk = ImageTk.PhotoImage(system_image)
            system_image_label = tk.Label(root, image=root.system_image_tk)
            system_image_label.place(relx=0.6, rely=0.1)
        except FileNotFoundError:
            pass

        # Add canvas for system visualization - DYNAMIC
        system_image_label = tk.Label(root, text="Current System:", font=standard_font_1_bold)
        system_image_label.place(relx=0.25, rely=0.05)
        self.canvas = tk.Canvas(root, width=WindForceGUI.CANVAS_MAIN_WIDTH, height=WindForceGUI.CANVAS_MAIN_HEIGHT,
                                bg="gray")
        self.canvas.place(relx=0.25, rely=0.1)
        self.add_canvas_static_elements()

        # Add buttons
        # Button CLEAR ALL
        button_clear = tk.Button(root, text="CLEAR ALL", command=self.clear_all,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=10, height=1)
        button_clear.place(relx=0.025, rely=0.05)
        # Button Program Info
        button_program_info = tk.Button(root, text="Info", command=self.program_info,
                                        font=('Arial', 8), width=8, height=1)
        button_program_info.place(relx=0.925, rely=0.015)

        # Buttons for input parameters
        buttons_input_params_label = tk.Label(root, text="System Parameters", font=standard_font_1_bold)
        buttons_input_params_label.place(relx=0.025, rely=0.125)
        # Button Enter Sections
        button_enter_sections = tk.Button(root, text="Sections", command=self.enter_sections,
                                          font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_sections.place(relx=0.025, rely=0.175)
        # Button Enter Springs
        button_enter_springs = tk.Button(root, text="Springs", command=self.enter_springs,
                                         font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_springs.place(relx=0.025, rely=0.225)
        # Button Enter Masses
        button_enter_masses = tk.Button(root, text="Masses", command=self.enter_masses,
                                        font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_masses.place(relx=0.025, rely=0.275)
        # Button Enter Forces
        button_enter_forces = tk.Button(root, text="Forces", command=self.enter_forces,
                                        font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_forces.place(relx=0.025, rely=0.325)
        # Button Enter Excentricity
        button_enter_excentricity = tk.Button(root, text="Excentricity", command=self.enter_excentricity,
                                              font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_excentricity.place(relx=0.025, rely=0.375)

        # Button open input file
        button_open_input = tk.Button(root, text="Open Input File", command=self.open_input_file,
                                      font=('Arial', 8), width=12, height=1)
        button_open_input.place(relx=0.025, rely=0.44)

        # Button save input file
        button_save_input = tk.Button(root, text="Save Input File", command=self.save_input_file,
                                      font=('Arial', 8), width=12, height=1)
        button_save_input.place(relx=0.025, rely=0.49)

        # Buttons for Calculation parameters
        buttons_input_calc_params_label = tk.Label(root, text="Calculation", font=standard_font_1_bold)
        buttons_input_calc_params_label.place(relx=0.025, rely=0.55)
        # Button Enter Calculation Parameters
        button_enter_calc_params = tk.Button(root, text="Calculation Parameter", command=self.enter_calc_params,
                                             font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_calc_params.place(relx=0.025, rely=0.6)
        # Button Start Calculation
        button_start_calculation = tk.Button(root, text="Start Calculation", command=self.start_calculation,
                                             font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_start_calculation.place(relx=0.025, rely=0.65)

        # Current system information in bottom - DYNAMIC
        current_system_information_label = tk.Label(root, text="System Information:", font=standard_font_1_bold)
        current_system_information_label.place(relx=0.025, rely=0.7)
        self.initial_system_information = f"Enter system parameters first. Values not set manually will be set to 0."
        self.current_system_information = tk.Text(self, height=8, width=140, wrap=tk.WORD,
                                                  font=WindForceGUI.STANDARD_FONT_2, bg='light gray', fg='black')
        self.current_system_information.place(relx=0.025, rely=0.75)
        self.current_system_information.insert(tk.END, self.initial_system_information)
        self.current_system_information.config(state='disabled')

    def update_current_system_info(self):
        """
        updates the sytem information in lower part of main window
        :return:
        """
        new_string = str(self.input_parameters) # todo
        self.current_system_information.config(state='normal')
        self.current_system_information.delete("1.0", tk.END)
        self.current_system_information.insert(tk.END, new_string)
        self.current_system_information.config(state='disabled')

    def add_canvas_static_elements(self):
        width = WindForceGUI.CANVAS_MAIN_WIDTH
        height = WindForceGUI.CANVAS_MAIN_HEIGHT
        gridspace = 20
        for x in range(gridspace, width, gridspace):
            self.canvas.create_line(x, 0, x, height, fill="dark gray", width=1)
        for y in range(gridspace, height, gridspace):
            self.canvas.create_line(0, y, width, y, fill="dark gray", width=1)
        self.canvas.create_line(1, 1, width, 1, fill='dark blue', width=4)
        self.canvas.create_line(1, 0, 1, height, fill='dark blue', width=6)
        self.canvas.create_line(0, height + 1, width, height + 1, fill='dark blue', width=2)
        self.canvas.create_line(width + 1, 0, width + 1, height, fill='dark blue', width=2)

    def add_canvas_solution_static_elements(self):
        width = self.canvas_sol_w
        height = self.canvas_sol_h
        gridspace = 20
        for x in range(gridspace, width, gridspace):
            self.canvas_solution.create_line(x, 0, x, height, fill="dark gray", width=1)
        for y in range(gridspace, height, gridspace):
            self.canvas_solution.create_line(0, y, width, y, fill="dark gray", width=1)
        self.canvas_solution.create_line(1, 1, width, 1, fill='dark blue', width=4)
        self.canvas_solution.create_line(1, 0, 1, height, fill='dark blue', width=6)
        self.canvas_solution.create_line(0, height + 1, width, height + 1, fill='dark blue', width=2)
        self.canvas_solution.create_line(width + 1, 0, width + 1, height, fill='dark blue', width=2)

    def open_input_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")],
            title="Open Input File",
        )
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            self.input_parameters = eval(content)  # todo: change to json
            self.update_current_system_info()


    def save_input_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Input As",
        )
        if file_path:
            with open(file_path, "w") as file:
                file.write(str(self.input_parameters))  # todo: change to json

    def input_window_boiler(self, input_type: str, *input_value_list):
        """
        boilerplate window for all input parameters except sections, gets arguments from buttons enter_springs() etc.
        :param input_type: first argument from button -> dict key in self.input_parameters
        :param input_value_list: further arguments from button -> dict values in self.input_parameters
        :return:
        """

        def get_input():
            """
            sets input variables in self.input_porameters, 0 if none given or string entered instead of int/float
            """
            nvalue = 0
            for value_type, entry_value in zip(input_value_list, self.entry_fields):
                value = entry_value.get()
                try:
                    value = float(value)
                except ValueError: # if user enters string
                    self.value_vars[nvalue].set('0')
                    value = 0
                self.input_parameters[input_type][value_type] = value
                nvalue += 1
            self.update_current_system_info() # todo

        # label_dict to replace dict entry with text for entry fields e.g fem_nbr_eigen_freq todo: wording...
        label_dict ={'base_cx': 'base_cx',
                     'base_cy': 'base_cy',
                     'base_phix': 'base_phix',
                     'base_phiy': 'base_phiy',
                     'head_cx': 'head_cx',
                     'base_m': 'base_m',
                     'head_m': 'head_m',
                     'freq_excite': 'freq_excite',
                     'f_head': 'f_head',
                     'm_head': 'm_head',
                     'freq_rotor': 'freq_rotor',
                     'qu_impulse': 'qu_impulse',
                     'qo_impulse': 'qo_impulse',
                     'nbr_periods': 'nbr_periods',
                     'delta_t': 'delta_t',
                     'num_1': 'num_1',
                     'num_2': 'num_2',
                     'exc_ex': 'exc_ex',
                     'exc_EA': 'exc_EA',
                     'exc_EIy': 'exc_EIy',
                     'exc_EIz': 'exc_EIz',
                     'exc_GIt': 'exc_GIt',
                     'exc_mass_unit': 'exc_mass_unit',
                     'exc_area': 'exc_area',
                     'exc_Ip': 'exc_Ip',
                     'fem_density': 'fem_density',
                     'fem_nbr_eigen_freq': 'Nbr of Eigenfreq',
                     'fem_dmas': 'fem_dmas',
                     'fem_exc': 'fem_exc'}

        window_size_y = len(input_value_list) * 55 if len(input_value_list) > 3 else (len(input_value_list) + 1) * 55

        input_window = tk.Toplevel(self)
        input_window.title(input_type)
        input_window.geometry(f"{350}x{window_size_y}")
        standard_font_1_bold = tkFont.Font(family="Arial", size=12, weight='bold')

        value_type_dict = {'springs': ['Enter Springs Parameters'],
                           'masses': ['Enter Masses Parameters'],
                           'forces': ['Enter Forces Parameters'],
                           'excentricity': ['Enter Excentricity Parameters'],
                           'calculation_param': ['Enter Calculation Parameters']}

        input_label = tk.Label(input_window, text=value_type_dict[input_type][0], font=standard_font_1_bold)
        input_label.place(relx=0.05, rely=0.05)

        rely = 0.15 if len(input_value_list) > 3 else 0.25
        rely_plus = 1 / len(input_value_list) * 0.5

        self.entry_fields = list()
        self.value_vars = list()
        for n_value, button_text in enumerate(input_value_list):
            # label
            entry_label = tk.Label(input_window, text=label_dict[button_text], font=("Arial", 12))
            entry_label.place(relx=0.05, rely=rely)

            # entry field
            self.value_var = tk.StringVar()
            self.value_var.set('0')
            self.entry_field = tk.Entry(input_window, textvariable=self.value_var, font=("Arial", 10), width=15)
            self.entry_field.place(relx=0.45, rely=rely)
            self.entry_fields.append(self.entry_field)
            self.value_vars.append(self.value_var)
            rely += rely_plus

        # set entry button
        set_entry_button = tk.Button(input_window, text="Set Input", command=get_input,
                                     font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        set_entry_button.place(relx=0.05, rely=rely)

    def clear_all(self):
        pass

    def enter_sections(self):
        pass

    def enter_springs(self):
        self.input_window_boiler('springs', 'base_cx', 'base_cy', 'base_phix', 'base_phiy', 'head_cx')

    def enter_masses(self):
        self.input_window_boiler('masses', 'base_m', 'head_m')

    def enter_forces(self):
        self.input_window_boiler('forces', 'freq_excite', 'f_head', 'freq_rotor', 'qu_impulse',
                                 'qo_impulse', 'nbr_periods', 'delta_t', 'num_1', 'num_2')

    def enter_excentricity(self):
        self.input_window_boiler('excentricity', 'exc_ex', 'exc_EA', 'exc_EIy', 'exc_EIz', 'exc_GIt', 'exc_mass_unit',
                                 'exc_area', 'exc_Ip')

    def enter_calc_params(self):
        self.input_window_boiler('calculation_param', 'fem_density', 'fem_nbr_eigen_freq', 'fem_dmas', 'fem_exc')

    def draw_solution(self, solution_nodes):

        def get_color_from_position(point_x_position):
            if point_x_position > 1:
                point_x_position = 1
            red = int(255 * point_x_position)
            blue = int(255 * (1 - point_x_position))
            green = 0
            color_code = "#{:02X}{:02X}{:02X}".format(red, green, blue)

            return color_code

        self.canvas_solution.create_line(self.canvas_sol_w / 2, self.canvas_sol_h, self.canvas_sol_w / 2,
                                         solution_nodes[-1][1],
                                         fill='dark green', width=2)

        for start_point, end_point in zip(solution_nodes[1:], solution_nodes[:-1]):
            # todo There might be an error here with the transformation mapping...
            color_scale_factor = 8
            normalized_position_start_x = (start_point[0] / self.canvas_sol_w + (
                    self.canvas_sol_w / 2) / self.canvas_sol_w) / 2
            normalized_position_end_x = (end_point[0] / self.canvas_sol_w + (
                    self.canvas_sol_w / 2) / self.canvas_sol_w) / 2
            if abs(0.5 - normalized_position_start_x) >= abs(0.5 - normalized_position_end_x):
                color_code = get_color_from_position(abs(normalized_position_start_x - 0.5) * color_scale_factor)
            else:
                color_code = get_color_from_position(abs(normalized_position_end_x - 0.5) * color_scale_factor)

            self.canvas_solution.create_line(start_point[0], start_point[1], end_point[0], end_point[1],
                                             fill=color_code, width=6)

    def transform_solution(self, solution_nodes):
        canvas_sol_w = self.canvas_sol_w
        canvas_sol_h = self.canvas_sol_h

        canvas_sol_w = math.floor(canvas_sol_w * 3 / 4)
        canvas_sol_h = math.floor(canvas_sol_h * 3 / 4)

        sol_x = [p[0] for p in solution_nodes]
        sol_y = [p[1] for p in solution_nodes]
        min_x = min(sol_x)
        max_x = max(sol_x)
        min_y = min(sol_y)
        max_y = max(sol_y)
        dist_x = max_x - min_x
        dist_y = max_y - min_y

        solution_nodes_transformed = [[math.floor(elem[0] / dist_x * canvas_sol_w / 3 + self.canvas_sol_w / 2),
                                       -elem[1] / dist_y * canvas_sol_h + self.canvas_sol_h] for elem in solution_nodes]

        return solution_nodes_transformed

    def interpolate_list(self, node_list: list) -> list:
        """
        interpolates between nodes for better visualization for lower resolution
        :param node_list:
        :return:
        """
        if len(node_list) < 100:
            x_data, y_data = zip(*node_list)
            x_data = np.array(x_data)
            y_data = np.array(y_data)
            y_interpolation = np.linspace(min(y_data), max(y_data), num=100)
            x_interpolation = np.interp(y_interpolation, y_data, x_data)
            new_list = list(zip(x_interpolation, y_interpolation))

            return [[x, y] for x, y in new_list]
        else:
            return node_list

    def start_calculation(self):
        """
        todo
        :return:
        """

        def update_solution(*args):
            eigen_freq_selected = solution_eigen_freq_selected.get()
            eigen_freq_selected = eigen_freq_selected.split('Eigenfreq.: ')[-1]
            solution = self.solution
            eigen_freq_selected = solution.get(int(eigen_freq_selected), None)

            if not eigen_freq_selected:
                print("Debug: Fehler bei Eigenfrequenzwahl")

            eigen_freq_selected_freq = eigen_freq_selected['eigenfreq']
            solution_nodes = eigen_freq_selected['solution']
            solution_nodes = self.interpolate_list(solution_nodes)
            solution_nodes_trans = self.transform_solution(solution_nodes)

            # update text
            self.selected_eigen_freq.set(eigen_freq_selected_freq)
            # update graphiocs
            all_canvas_elements = self.canvas_solution.find_all()
            for elem in all_canvas_elements:
                self.canvas_solution.delete(elem)
            self.add_canvas_solution_static_elements()
            self.draw_solution(solution_nodes_trans)

        def button_save_output():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save Output As",
            )
            if file_path:
                with open(file_path, "w") as file:
                    file.write(self.solution)

        # updates system information
        self.update_current_system_info()

        # creates FEM Solution window
        fem_solution_window = tk.Toplevel(self)
        fem_solution_window.title("FEM Solution")
        fem_solution_window.geometry(f"{600}x{600}")

        # graphical output
        self.canvas_sol_w = 400
        self.canvas_sol_h = 550
        self.canvas_solution = tk.Canvas(fem_solution_window, width=self.canvas_sol_w, height=self.canvas_sol_h,
                                         bg="gray")
        self.canvas_solution.place(relx=200 / 600 - 0.025, rely=(1 - (550 / 600)) / 2)
        self.add_canvas_solution_static_elements()

        # Selector for eigenfrequency
        solution_eigen_freq_label = tk.Label(fem_solution_window, text="Select Eigenfrequency",
                                             font=WindForceGUI.STANDARD_FONT_1)
        solution_eigen_freq_label.place(relx=0.025, rely=0.025)
        solution_eigen_freqs_nbr = sorted(list(self.solution.keys()))
        solution_calculated_eigen_freqs = [f"Eigenfreq.: {ef_nbr}" for ef_nbr in solution_eigen_freqs_nbr]
        solution_eigen_freq_selected = tk.StringVar()
        solution_eigen_freq_selected.set(solution_calculated_eigen_freqs[0])  # default value
        dropdown_solution_eigen_freq = tk.OptionMenu(fem_solution_window, solution_eigen_freq_selected,
                                                     *solution_calculated_eigen_freqs)
        dropdown_solution_eigen_freq.place(relx=0.025, rely=0.075)
        solution_eigen_freq_selected.trace('w', update_solution)

        # Show Eigenfrequency
        self.selected_eigen_freq = tk.StringVar()
        self.selected_eigen_freq.set('None')
        selected_eigen_freq_label = tk.Entry(fem_solution_window, textvariable=self.selected_eigen_freq,
                                             state='readonly', font=("Arial", 10), width=15)
        selected_eigen_freq_label.place(relx=0.025, rely=0.135)

        # Button save output
        button_save_output = tk.Button(fem_solution_window, text="Save Output ", command=button_save_output,
                                       font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_save_output.place(relx=0.025, rely=0.85)

        # Solution first Eigenfrequency
        update_solution()

        # if self.solution is not None:
        #     ...

    def program_info(self):
        info_window = tk.Toplevel(self)
        info_window.title("Info")
        info_str = f"Info:\n\n" \
                   f"Version: {VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}\n" \
                   f"Authors: {AUTHOR}\n"
        info_label = tk.Label(info_window, text=info_str, font=WindForceGUI.STANDARD_FONT_2)
        info_label.place(relx=0.025, rely=0.1)

    def development(self):
        return_values = {0: {'eigenfreq': 15,
                             'solution': [[0, 0], [0.1, 0.5], [0.2, 1],
                                          [0.15, 1.5], [0.05, 2], [0, 2.5],
                                          [-0.05, 3], [-0.1, 3.5], [-0.2, 4]]},
                         1: {'eigenfreq': 35,
                             'solution': [[0, 0], [0.2, 0.5], [0.4, 1],
                                          [0.3, 1.5], [0.1, 2], [0, 2.5],
                                          [-0.1, 3], [-0.2, 3.5], [-3, 4]]},
                         2: {'eigenfreq': 155,
                             'solution': [[0, 0], [0.1, 0.5], [-0.2, 1],
                                          [0.15, 1.5], [-0.05, 2], [0, 2.5],
                                          [0.05, 3], [-0.1, 3.5], [0.2, 4]]},
                         }
        self.solution = return_values


if __name__ == '__main__':
    gui = WindForceGUI()
    gui.development()  # set solution for development before starting mainloop
    gui.mainloop()
