from operator import itemgetter

import units, pygame

Human = 0
AI = 1


class Game:

    class WinnerChecker:
        """
        The idea is to store amount of units for each player on each row, column and diagonal
        And then make simple short check when this amount is exactly the winning amount
        But if there some line has units more than need to win,
        we just go through this line to perform some extra checkups
        """
        def __init__(self, size, win_size):

            self._move_count = 0

            self._size = size
            self._win_size = win_size

            self._rows = {
                units.Cross: [0] * size,
                units.Nought: [0] * size
            }
            self._cols = {
                units.Cross: [0] * size,
                units.Nought: [0] * size
            }
            self._diags_count = (size - win_size) * 2 + 1
            self._diags = {
                units.Cross: [0] * self._diags_count,
                units.Nought: [0] * self._diags_count
            }
            self._anti_diags = {
                units.Cross: [0] * self._diags_count,
                units.Nought: [0] * self._diags_count
            }

            # Mapping between coordinates on game field and the indexes of diagonals that they belongs to
            # Using that property that:
            #   if points (x0,y0) and (x1, y1) on the same diagonal,
            #   then |x0 -/+ y0| = |x1 -/+ y1|
            self._diags_index = {}
            self._anti_diags_index = {}
            for i in range(size):
                for j in range(size):
                    self._diags_index[i, j] = i - j + (self._size - self._win_size)  # This part to set up range(0, diags_count)
                    self._anti_diags_index[i, j] = i + j - (self._win_size - 1)  # This part to set up range(0, diags_count)

        def register_move(self, pos, player):
            x, y = pos

            self._cols[player][x] += 1
            self._rows[player][y] += 1

            diag = self._diags_index[x, y]
            anti_diag = self._anti_diags_index[x, y]

            if 0 <= diag < self._diags_count:
                self._diags[player][diag] += 1

            if 0 <= anti_diag < self._diags_count:
                self._anti_diags[player][anti_diag] += 1

            self._move_count += 1

        def _simple_row_check(self, row, player):
            n = 0
            for cell in row:
                if cell == player:
                    break
                n += 1
            for cell in reversed(row):
                if cell == player:
                    break
                n += 1
            # This condition means that all units are in a row
            # n - total amount of indents from both sides
            # it must be equal to the rest of cells
            if n == len(row) - self._win_size:
                raise GameOver(player)

        def _extra_row_check(self, row, player):
            started = False
            n = 0
            for cell in row:
                if cell == player:
                    if not started:
                        started = True
                    n += 1
                elif started:
                    # Just checking every sequence on our way to be length of winning amount
                    if n == self._win_size:
                        raise GameOver(player)
                    n = 0
                    started = False

        def check_winner(self, field, player):
            if self._move_count >= self._win_size * 2 - 1:
                for i in range(self._size):

                    # Pack together the stored value for the row(col ect) and the actual row itself
                    # for easy iterating over it
                    zip = (
                        (self._rows[player][i], [field[x][i] for x in range(self._size)]),
                        (self._cols[player][i], [field[i][y] for y in range(self._size)])
                    )

                    for n, row in zip:
                        if n == self._win_size:
                            self._simple_row_check(row, player)
                        elif n > self._win_size:
                            self._extra_row_check(row, player)

                for i in range(self._diags_count):

                    # The same packing, but with diagonals
                    zip = (
                        (
                            self._diags[player][i],
                            [field[x][y] for (x, y), index in sorted(
                                self._diags_index.items(),
                                key=itemgetter(0)
                            ) if index == i]
                        ),
                        (
                            self._anti_diags[player][i],
                            [field[x][y] for (x, y), index in sorted(
                                self._anti_diags_index.items(),
                                key=itemgetter(0)
                            ) if index == i]
                        )
                    )

                    for n, row in zip:
                        if n == self._win_size:
                            self._simple_row_check(row, player)
                        elif n > self._win_size:
                            self._extra_row_check(row, player)

    def __init__(self, field_size=3, win_size=3, players=(Human, Human)):
        if win_size < 3:
            win_size = 3
        elif win_size > field_size:
            win_size = field_size

        self._players = {
            units.Cross: players[0],
            units.Nought: players[1]
        }
        self._current_player = units.Cross  # always first

        # Create logical game field
        self._field_size = field_size
        self._field = [[None for x in range(field_size)] for y in range(field_size)]

        # Set up surface for game field
        self._screen_size = pygame.display.get_surface().get_rect()
        self._field_surface = pygame.Surface((
            self._screen_size.width,
            self._screen_size.height
        )).convert()

        self._unit_size = (
            int(self._screen_size.width / field_size),
            int(self._screen_size.height / field_size)
        )

        # Create image of game field
        self._create_field_surface()

        # Create groups for game units
        self._crosses = pygame.sprite.RenderUpdates()
        self._noughts = pygame.sprite.RenderUpdates()

        # Pre-computing of mapping between logical and pixels positions
        self._map = {}
        self._compute_map()

        # Data for checking winner
        self._winner_checker = Game.WinnerChecker(field_size, win_size)

    def _create_field_surface(self):
        self._field_surface.fill((255, 255, 255))

        draw_pointer_x = self._unit_size[0]
        draw_pointer_y = self._unit_size[1]

        for i in range(self._field_size - 1):
            pygame.draw.line(
                self._field_surface,
                (0, 0, 0),
                (draw_pointer_x, 0),
                (draw_pointer_x, self._screen_size.height),
                int(self._unit_size[0] * 0.08)
            )
            pygame.draw.line(
                self._field_surface,
                (0, 0, 0),
                (0, draw_pointer_y),
                (self._screen_size.width, draw_pointer_y),
                int(self._unit_size[0] * 0.08)
            )
            draw_pointer_x += self._unit_size[0]
            draw_pointer_y += self._unit_size[1]

    def _compute_map(self):
        for i in range(self._field_size):
            for j in range(self._field_size):
                self._map[i, j] = pygame.Rect((
                    int(self._screen_size.width * (i / self._field_size)),
                    int(self._screen_size.height * (j / self._field_size))
                ), self._unit_size)

    def _on_mouse_click(self, event):
        # Check for possibility to make move
        if self._players[self._current_player] == Human:
            # Unmap event.pos
            for pos, field in self._map.items():
                if field.collidepoint(event.pos):
                    self.place_unit(pos)
                    break

    def _on_key_pressed(self, event):
        pass

    def player_input(self, events):
        for event in events:
            if event.type == pygame.KEYUP:
                self._on_key_pressed(event)
            if event.type == pygame.MOUSEBUTTONUP:
                self._on_mouse_click(event)

    def update(self):
        # Draw all units at right places
        self._crosses.update(self._map)
        self._noughts.update(self._map)

    def draw(self, screen):
        screen.blit(self._field_surface, (0, 0))
        self._crosses.draw(screen)
        self._noughts.draw(screen)

    def get_current_player(self):
        return self._players[self._current_player]

    def get_current_state(self):
        return self._field

    def place_unit(self, pos):
        x, y = pos
        # Check if the cell is free to place here
        if self._field[x][y] is None:
            self._winner_checker.register_move(pos, self._current_player)

            # Logical placing of unit
            self._field[x][y] = self._current_player

            # Add unit to corresponding sprite group
            group = self._crosses \
                if self._current_player == units.Cross \
                else self._noughts
            group.add(units.Unit(self._current_player, pos, self._unit_size))

            # Check winner
            try:
                self._winner_checker.check_winner(self._field, self._current_player)
            finally:
                self.update()

            # Switch player
            self._current_player ^= units.Cross  # using xor properties


class GameOver(Exception):

    def __init__(self, winner):
        super().__init__()
        self.winner = winner

    def __str__(self):
        return ('Crosses' if self.winner == units.Cross else 'Noughts') + ' wins!'
