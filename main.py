import sys, pygame

from game import Game, Human, AI, GameOver

pygame.init()

field_size, size_of_win_row, players_mode = 20, 5, (Human, Human)

size = width, height = 700, 700
screen = pygame.display.set_mode(size)


def game_over_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYUP:
                return

        pygame.display.flip()


def game_loop(game):
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()

        # Handle players input
        game.player_input(events)

        if game.get_current_player() == AI:
            # Give chance to AI
            # pass to AI game.get_current_state()
            # pass to game.place_unit() AI decision
            pass

        game.draw(screen)

        pygame.display.flip()

# Main loop
while True:
    game = Game(field_size, size_of_win_row, players_mode)
    try:
        game_loop(game)
    except GameOver as e:
        game.draw(screen)
        message = pygame.font.Font(None, 100).render(str(e), 1, (0, 0, 255))
        message_rect = message.get_rect(
            centerx=screen.get_width()/2,
            centery=screen.get_height()/2
        )
        screen.blit(message, message_rect)
        game_over_screen()
