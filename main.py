import sqlite3, pygame, sys, random, ctypes

pygame.init()                                   # Initial Pygame
screen = pygame.display.set_mode((576,1024))    # Set Screen
clock = pygame.time.Clock()                     # Set Frame Rate
font = pygame.font.Font('content/ttf/04B_19.TTF',60)
play_font = pygame.font.Font('content/ttf/04B_19.TTF',80)
pygame.display.set_caption("Flappy Bird")
Icon = pygame.image.load('content/icos/Flappy_Bird.png')
pygame.display.set_icon(Icon)

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# ---------------- VARIABLES ----------------
gravity = 0.25
game_active = False
nr_score = 0
nr_high_score = 0
show = True
select_line = 0
select_field_player = 0
select_field_mode = 0
select_field_pipe = 0
tick = 120
# ------------- END - VARIABLES -------------


# ---------------- SQL ----------------
# Verbindung zum MySQL-Server herstellen
cnx = mysql.connector.connect(
    user='flappydb',
    password='FlappyBirdDB23',
    host='localhost',
    database='flappybird'
)
# ---------------- END - SQL ----------


# ---------------- IMAGES ----------------
background = pygame.image.load("content/world/background-day.png").convert()    # Convert for Pygame
background = pygame.transform.scale2x(background)                               # Double the Size of BG
background_x = 0

floor = pygame.image.load("content/world/base.png").convert()
floor = pygame.transform.scale2x(floor)
floor_x = 0
# ------------- END - IMAGES -------------


# ---------------- PLAYER ----------------
#player = pygame.image.load("content/player/yellowbird-midflap.png").convert_alpha()
#player = pygame.transform.scale2x(player)
#player_rect = player.get_rect(center=(100,512))

player_up = pygame.transform.scale2x(pygame.image.load("content/player/yellowbird-upflap.png").convert_alpha())
player_mid = pygame.transform.scale2x(pygame.image.load("content/player/yellowbird-midflap.png").convert_alpha())
player_down = pygame.transform.scale2x(pygame.image.load("content/player/yellowbird-downflap.png").convert_alpha())
player_frames = [player_up, player_mid, player_down]
player_index = 0
player = player_frames[player_index]
player_rect = player.get_rect(center = (100,523))                                # Create Rectangle for Player Collision
player_move = 0

player_rect_select = player.get_rect(center=(288, 512))
player_selection = 0

FLY = pygame.USEREVENT + 1
pygame.time.set_timer(FLY, 200)
# ------------- END - PLAYER -------------


# ---------------- PIPES ----------------
pipe_img = pygame.image.load("content/world/pipe-green.png")
pipe_img = pygame.transform.scale2x(pipe_img)

pipe_small_green = pygame.image.load("content/world/pipe-green-small.png").convert_alpha()
pipe_small_green_rect = pipe_small_green.get_rect(center=(288, 512))
pipe_small_red = pygame.image.load("content/world/pipe-red-small.png").convert_alpha()
pipe_small_red_rect = pipe_small_red.get_rect(center=(288, 512))

pipe_list = []
pipe_height = [400, 600, 800]

SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
# ------------- END - PIPES -------------


# ---------------- GAMEOVER ----------------
gameover = pygame.transform.scale2x(pygame.image.load("content/world/message.png").convert_alpha())
gameover_rect = gameover.get_rect(center = (288, 420))
# ------------- END - GAMEOVER -------------


# ---------------- DAY/NIGHT ----------------
day = pygame.image.load("content/world/sun.png").convert_alpha()
day_rect = day.get_rect(center=(288, 512))

night = pygame.image.load("content/world/moon.png").convert_alpha()
night_rect = night.get_rect(center=(288, 512))
# ------------- END - DAY/NIGHT -------------


# ---------------- SOUNDS ----------------
flap_sound = pygame.mixer.Sound("content/audio/wing.wav")
flap_sound.set_volume(0.05)

death_sound = pygame.mixer.Sound("content/audio/hit.wav")
death_sound.set_volume(0.05)

score_sound = pygame.mixer.Sound("content/audio/point.wav")
score_sound.set_volume(0.05)
score_sound_countdown = 500

start_scound = pygame.mixer.Sound("content/audio/swoosh.wav")
start_scound.set_volume(0.05)

fall_sound = pygame.mixer.Sound('content/audio/die.wav')
fall_sound.set_volume(0.05)
# ------------- END - SOUNDS -------------


# ---------------- BACKGROUND MUSIC ----------------
r = random.randint(1, 4)

if r == 1:
    theme = pygame.mixer.Sound('content/audio/bgm/Fredji_Happy_Life.mp3')
    theme.set_volume(0.01)
    theme.play(-1)
elif r == 2:
    theme = pygame.mixer.Sound('content/audio/bgm/Ikson_New_Day.mp3')
    theme.set_volume(0.01)
    theme.play(-1)
elif r == 3:
    theme = pygame.mixer.Sound('content/audio/bgm/Jarico_Island.mp3')
    theme.set_volume(0.01)
    theme.play(-1)
elif r == 4:
    theme = pygame.mixer.Sound('content/audio/bgm/Jarico_Landscape.mp3')
    theme.set_volume(0.01)
    theme.play(-1)
# ------------- END - BACKGROUND MUSIC -------------


# ---------------- FUNCTIONS ----------------
def draw_floor():
    screen.blit(floor, (floor_x, 900))
    screen.blit(floor, (floor_x + 576, 900))


def draw_background():
    screen.blit(background, (background_x, 0))
    screen.blit(background, (background_x + 576, 0))


def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bot_pipe = pipe_img.get_rect(midtop=(700, random_pipe_pos))
    top_pipe = pipe_img.get_rect(midbottom = (700, random_pipe_pos - 300))
    return bot_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_img, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_img, False, True)
            screen.blit(flip_pipe, pipe)


def check_collision(pipes):
    for pipe in pipes:
        if player_rect.colliderect(pipe):
            death_sound.play()
            return False

    if player_rect.top <= -100 or player_rect.bottom >= 900:
        fall_sound.play()
        return False

    return True


def rotated_player(player):
    new_player = pygame.transform.rotozoom(player, -player_move*3, 1)
    return new_player


def player_animation():
    new_player = player_frames[player_index]
    new_player_rect = new_player.get_rect(center= (100, player_rect.centery))
    return new_player, new_player_rect


def score_display(game_state):
    if game_state == 'main_game':
        score = font.render(str(int(nr_score)), True, (255, 255, 255))
        score_rect = score.get_rect(center = (288, 100))
        screen.blit(score, score_rect)

    if game_state == 'game_over':
        score = font.render(f'Score: {int(nr_score)}', True, (255, 255, 255))
        score_rect = score.get_rect(center=(288, 100))
        screen.blit(score, score_rect)

        high_score = font.render(f'High Score: {int(nr_high_score)}', True, (255, 255, 255))
        high_score_rect = high_score.get_rect(center=(288, 850))
        screen.blit(high_score, high_score_rect)


def update_score(nr_score, nr_high_score):
    if nr_score > nr_high_score:
        nr_high_score = nr_score

    return nr_high_score
# ------------- END - FUNCTIONS -------------






############################ GAME LOOP ############################
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  # Shutdown Game

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_SPACE and game_active:
                player_move = 0
                player_move -= 10
                flap_sound.play()

            if event.key == pygame.K_RETURN and game_active == False:
                pipe_list.clear()
                player_rect.center = (100, 512)
                player_move = 0
                nr_score = 0
                score_sound_countdown = 500
                start_scound.play()
                game_active = True

            if event.key == pygame.K_LEFT or event.key == pygame.K_a and game_active == False:
                if select_line == 0:
                    if select_field_player < 2:
                        select_field_player += 1
                    else:
                        select_field_player = 0
                elif select_line == 1:
                    if select_field_mode < 1:
                        select_field_mode += 1
                    else:
                        select_field_mode = 0
                elif select_line == 2:
                    if select_field_pipe < 1:
                        select_field_pipe += 1
                    else:
                        select_field_pipe = 0

            if event.key == pygame.K_RIGHT or event.key == pygame.K_d and game_active == False:
                if select_line == 0:
                    if select_field_player > 0:
                        select_field_player -= 1
                    else:
                        select_field_player = 2
                elif select_line == 1:
                    if select_field_mode > 0:
                        select_field_mode -= 1
                    else:
                        select_field_mode = 1
                elif select_line == 2:
                    if select_field_pipe > 0:
                        select_field_pipe -= 1
                    else:
                        select_field_pipe = 1


            if event.key == pygame.K_UP or event.key == pygame.K_w and game_active == False:
                    if select_line < 2:
                        select_line += 1
                    else:
                        select_line = 0

            if event.key == pygame.K_DOWN or event.key == pygame.K_s and game_active == False:
                if select_line > 0:
                    select_line -= 1
                else:
                    select_line = 2

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == FLY:
            if player_index < 2:
                player_index += 1
            else:
                player_index = 0

            player, player_rect = player_animation()

    # BACKGROUND
    background_x -= 0.5
    draw_background()
    if background_x <= -576:
        background_x = 0
    screen.blit(background, (background_x,0))


    if game_active == True:
        # PLAYER
        player_move += gravity
        rotate_player = rotated_player(player)
        player_rect.centery += player_move
        screen.blit(rotate_player, player_rect)
        game_active = check_collision(pipe_list)


        # PIPES
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        #Score
        nr_score += 0.01
        score_display('main_game')
        score_sound_countdown -= 1
        if score_sound_countdown <= 0:
            score_sound.play()
            score_sound_countdown = 500

        select_line = 0
        tick += 0.01
    else:
        arrow_left = font.render('<', True, (255, 255, 255))
        arrow_left_rect = arrow_left.get_rect(center=(150, 515))
        screen.blit(arrow_left, arrow_left_rect)

        arrow_right = font.render('>', True, (255, 255, 255))
        arrow_right_rect = arrow_right.get_rect(center=(426, 515))
        screen.blit(arrow_right, arrow_right_rect)

        screen.blit(gameover, gameover_rect)
        nr_high_score = update_score(nr_score, nr_high_score)
        score_display('game_over')

        tick = 120

        if select_line == 0:
            if select_field_player == 0:
                player_up = pygame.transform.scale2x(
                    pygame.image.load("content/player/yellowbird-upflap.png").convert_alpha())
                player_mid = pygame.transform.scale2x(
                    pygame.image.load("content/player/yellowbird-midflap.png").convert_alpha())
                player_down = pygame.transform.scale2x(
                    pygame.image.load("content/player/yellowbird-downflap.png").convert_alpha())
                player_frames = [player_up, player_mid, player_down]
                screen.blit(player, player_rect_select)

            elif select_field_player == 1:
                player_up = pygame.transform.scale2x(
                    pygame.image.load("content/player/bluebird-upflap.png").convert_alpha())
                player_mid = pygame.transform.scale2x(
                    pygame.image.load("content/player/bluebird-midflap.png").convert_alpha())
                player_down = pygame.transform.scale2x(
                    pygame.image.load("content/player/bluebird-downflap.png").convert_alpha())
                player_frames = [player_up, player_mid, player_down]
                screen.blit(player, player_rect_select)

            elif select_field_player == 2:
                player_up = pygame.transform.scale2x(
                    pygame.image.load("content/player/redbird-upflap.png").convert_alpha())
                player_mid = pygame.transform.scale2x(
                    pygame.image.load("content/player/redbird-midflap.png").convert_alpha())
                player_down = pygame.transform.scale2x(
                    pygame.image.load("content/player/redbird-downflap.png").convert_alpha())
                player_frames = [player_up, player_mid, player_down]
                screen.blit(player, player_rect_select)
        elif select_line == 1:
            if select_field_mode == 0:  # day
                background = pygame.image.load("content/world/background-day.png").convert()  # Convert for Pygame
                background = pygame.transform.scale2x(background)
                screen.blit(day, day_rect)

            elif select_field_mode == 1:  # night
                background = pygame.image.load("content/world/background-night.png").convert()  # Convert for Pygame
                background = pygame.transform.scale2x(background)
                screen.blit(night, night_rect)
        elif select_line == 2:
            if select_field_pipe == 0: # Green
                pipe_img = pygame.image.load("content/world/pipe-green.png")
                pipe_img = pygame.transform.scale2x(pipe_img)
                screen.blit(pipe_small_green, pipe_small_green_rect)

            elif select_field_pipe == 1: # Red
                pipe_img = pygame.image.load("content/world/pipe-red.png")
                pipe_img = pygame.transform.scale2x(pipe_img)
                screen.blit(pipe_small_red, pipe_small_red_rect)


    # FLOOR
    floor_x -= 1
    draw_floor()
    if floor_x <= -576:
        floor_x = 0
    screen.blit(floor, (floor_x,900))

    if game_active == False:
        play = font.render('Press ENTER', True, (255, 255, 255))
        play_rect = play.get_rect(center=(288, 950))
        screen.blit(play, play_rect)
        show = False

    pygame.display.update()
    clock.tick(tick)
######################### END - GAME LOOP #########################