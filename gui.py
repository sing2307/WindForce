import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont

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
        buttons_input_params_label.place(relx=0.025, rely=0.15)
        # Button Enter Sections
        button_enter_sections = tk.Button(root, text="Sections", command=self.enter_sections,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_sections.place(relx=0.025, rely=0.2)
        # Button Enter Springs
        button_enter_springs = tk.Button(root, text="Springs", command=self.enter_springs,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_springs.place(relx=0.025, rely=0.25)
        # Button Enter Masses
        button_enter_masses = tk.Button(root, text="Masses", command=self.enter_masses,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_masses.place(relx=0.025, rely=0.3)
        # Button Enter Forces
        button_enter_forces = tk.Button(root, text="Forces", command=self.enter_forces,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_forces.place(relx=0.025, rely=0.35)
        # Button Enter Excentricity
        button_enter_excentricity = tk.Button(root, text="Excentricity", command=self.enter_excentricity,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_excentricity.place(relx=0.025, rely=0.4)

        # Buttons for Calculation parameters
        buttons_input_calc_params_label = tk.Label(root, text="Calculation", font=standard_font_1_bold)
        buttons_input_calc_params_label.place(relx=0.025, rely=0.5)
        # Button Enter Calculation Parameters
        button_enter_calc_params = tk.Button(root, text="Calculation Parameter", command=self.enter_calc_params,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_enter_calc_params.place(relx=0.025, rely=0.55)
        # Button Start Calculation
        button_start_calculation = tk.Button(root, text="Start Calculation", command=self.start_calculation,
                                 font=WindForceGUI.STANDARD_FONT_BUTTON, width=18, height=1)
        button_start_calculation.place(relx=0.025, rely=0.6)

        # Current system information in bottom - DYNAMIC
        current_system_information_label = tk.Label(root, text="System Information:", font=standard_font_1_bold)
        current_system_information_label.place(relx=0.025, rely=0.7)
        initial_system_information = f"Some system information here\n like data for entered sections\netc."
        self.current_system_information = tk.Text(self, height=8, width=140, wrap=tk.WORD,
                                                  font=WindForceGUI.STANDARD_FONT_2, bg='light gray', fg='black')
        self.current_system_information.place(relx=0.025, rely=0.75)
        self.current_system_information.insert(tk.END, initial_system_information)
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


    def clear_all(self):
        pass

    def enter_sections(self):
        pass

    def enter_springs(self):
        pass

    def enter_masses(self):
        pass

    def enter_forces(self):
        pass

    def enter_excentricity(self):
        pass

    def enter_calc_params(self):
        pass

    def start_calculation(self):
        """
        todo
        :return:
        """

        # creates FEM Solution window
        fem_solution_window = tk.Toplevel(self)
        fem_solution_window.title("FEM Solution")
        fem_solution_window.geometry(f"{600}x{600}")

        # graphical output
        canvas_solution = tk.Canvas(fem_solution_window, width=400, height=550, bg="gray")
        canvas_solution.place(relx=200/600-0.025, rely=(1-(550/600))/2)

        # Selector for eigenfrequency
        solution_eigen_freq_label = tk.Label(fem_solution_window, text="Select Eigenfrequency", font=WindForceGUI.STANDARD_FONT_1)
        solution_eigen_freq_label.place(relx=0.025, rely=0.025)
        solution_eigen_freqs_nbr = sorted(list(self.solution.keys()))
        solution_calculated_eigen_freqs = [f"Eigenfreq.: {ef_nbr}" for ef_nbr in solution_eigen_freqs_nbr]
        solution_eigen_freq_selected = tk.StringVar()
        solution_eigen_freq_selected.set(solution_calculated_eigen_freqs[0])  # default value
        dropdown_solution_eigen_freq = tk.OptionMenu(fem_solution_window, solution_eigen_freq_selected,
                                                     *solution_calculated_eigen_freqs)
        dropdown_solution_eigen_freq.place(relx=0.025, rely=0.075)

        # Show Eigenfrequency
        selected_eigen_freq = tk.StringVar()
        selected_eigen_freq.set('None')
        selected_eigen_freq_label = tk.Entry(fem_solution_window, textvariable=selected_eigen_freq,
                                                 state='readonly', font=("Arial", 10), width=6)
        selected_eigen_freq_label.place(relx=0.025, rely=0.135)


        if self.solution is not None:
            ...


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
    gui.development() # set solution for development before starting mainloop
    gui.mainloop()

