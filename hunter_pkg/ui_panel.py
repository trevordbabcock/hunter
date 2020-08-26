from hunter_pkg import colors

class UIPanel():
    def __init__(self, x, y, height, width, hunter):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.hunter = hunter
        self.color = colors.dark_gray()

    def render(self, console):
        console.draw_rect(x=1, y=1, height=48, width=17, ch=1, bg=self.color)
        console.print(x=1, y=1, string=f"-.-.-.-.-.-.-.-.-", fg=colors.white())
        console.print(x=1, y=2, string=f".               .", fg=colors.white())
        console.print(x=1, y=3, string=f"-Entity: Hunter -", fg=colors.white())
        console.print(x=1, y=4, string=f".Hlth {self.hunter.curr_health}/{self.hunter.max_health}     .", fg=colors.white())
        console.print(x=1, y=5, string="-Hngr {:02.0f}/{}     -".format(self.hunter.curr_hunger, self.hunter.max_hunger), fg=colors.white())
        console.print(x=1, y=6, string=f".Nrgy {self.hunter.curr_energy}/{self.hunter.max_energy}     .", fg=colors.white())
        for i in range(7, 48, 2):
            console.print(x=1, y=i, string=f"-               -", fg=colors.white())
            console.print(x=1, y=i+1, string=f".               .", fg=colors.white())
        console.print(x=1, y=48, string=f"-.-.-.-.-.-.-.-.-", fg=colors.white())
