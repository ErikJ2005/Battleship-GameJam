from state import State

class MainMenu(State):
    def __init__(self, spill):
        super().__init__(spill)
        spill.screen.fill("black")
        spill.skriv_tekst(spill.screen, "Trykk return/enter for å starte", spill.font, (255, 255, 255), (spill.screen.get_width()//2, spill.screen.get_height()//2))
    
    def update(self):
        pass

    def render(self):
        pass