"""
Игра змейка на основе PyGame

В этой игре змейка движется по полю, собирая яблоки. Цель игры - собрать как можно больше яблок.
Дополнение - На поле генерируются стены, которые змейка не может пройти.

Игра заканчивается, если змейка врезается в стену или сама в себя.

Игра имеет 3 уровня сложности:
    1. Лёгкий - змейка движется с низкой скоростью, стены отсутствуют.
    2. Средний - змейка движется со средней скоростью, присутствуют случайные блоки.
    3. Сложный - змейка движется с высокой скоростью, присутствуют стены с разной длиной.
    4. Супер сложный - Могут появляться в случайное время, в случайном месте

При запуске игры пользователь попадает в меню, где может выбрать уровень сложности.
Так же в меню можно посмотреть рекорды, которые сохраняются в файле records.txt.

При нажатии на кнопку "Начать игру" игра начинается.


"""
import datetime
import sys
import time

import pygame
import random
import pygame_menu


class Snake:
    def __init__(self, x, y, length=1):
        """
        Инициализация змейки
        :param x: Координата x
        :param y: Координата y
        :param length: Длина змейки
        """
        self.x = x  # Координата x
        self.y = y  # Координата y
        self.length = length  # Длина змейки
        self.body = [[x, y] for i in range(length)]  # Тело змейки
        self.direction = random.choice(['right', 'left', 'up', 'down'])  # Случайное направление движения змейки
        self.score = 0  # Счёт игрока
        self.pill_timer = 0  # Таймер для пилюли

    def move(self):
        """
        Движение змейки
        :return:
        """
        if self.direction == 'right':
            self.x += 1
        elif self.direction == 'left':
            self.x -= 1
        elif self.direction == 'up':
            self.y -= 1
        elif self.direction == 'down':
            self.y += 1

        # Проверка на столкновение с самой собой
        self.body.insert(0, [self.x, self.y])
        self.body.pop()

    def add_body(self, points=1):
        """
        Добавление тела змейке
        :return:
        """
        self.length += 1
        self.body.append([self.x, self.y])
        self.score += points

    def eat_pill(self):
        """
        Съедание пилюли
        :return:
        """
        self.pill_timer = 120  # Устанавливаем таймер на 120 кадров

        self.length += 1
        self.body.append([self.x, self.y])
        self.score += 1

    def is_pill(self, with_update: bool = True):
        """
        Проверка на пилюлю
        :return:
        """
        if self.pill_timer > 0:
            if with_update:
                self.pill_timer -= 1
            return True
        else:
            return False


class Apple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.apple_image = pygame.image.load('apple.png').convert()
        self.apple_image = pygame.transform.scale(self.apple_image, (20, 20))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        surface.blit(self.apple_image, (self.x * 20, self.y * 20))


class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.block_image = pygame.image.load('block.png').convert()
        self.block_image = pygame.transform.scale(self.block_image, (20, 20))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        surface.blit(self.block_image, (self.x * 20, self.y * 20))


class Pill:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pill_image = pygame.image.load('pill.png').convert()
        self.pill_image = pygame.transform.scale(self.pill_image, (20, 20))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        surface.blit(self.pill_image, (self.x * 20, self.y * 20))


class FastPill:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fast_pill_image = pygame.image.load('fast_pill.png').convert()
        self.fast_pill_image = pygame.transform.scale(self.fast_pill_image, (20, 20))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        surface.blit(self.fast_pill_image, (self.x * 20, self.y * 20))


class Game:
    def __init__(self, width: int, height: int, difficulty: int = 1):
        self.blocks = []
        self.width = width
        self.height = height
        self.difficulty = difficulty  # 1 - лёгкий, 2 - средний, 3 - сложный, 4 - супер сложный
        self.display = pygame.display.set_mode((width * 20, height * 20))  # Создание окна
        self.pygame = pygame.init()  # Инициализация pygame
        self.snake = Snake(5, 5)  # Создание змейки
        self.block_size = 20
        self.clock_speed = 10
        self.apple = Apple(10, 10)
        self.pill = Pill(15, 15)
        self.fast_pill = FastPill(20, 20)
        self.font = pygame.font.SysFont('arial', 15)  # Шрифт
        self.menu = pygame_menu.Menu('Змейка', self.width * 20, self.height * 20,
                                     theme=pygame_menu.themes.THEME_GREEN)  # Создание меню
        self.menu.add.button('Начать играть', self.run_level_menu)
        self.menu.add.button('Рекорды', self.show_records)
        self.menu.add.button('Выйти', pygame_menu.events.EXIT)

        self.level_menu = pygame_menu.Menu('Выбор уровня сложности', self.width * 20, self.height * 20,
                                           theme=pygame_menu.themes.THEME_GREEN)

        self.level_menu.add.button('Легкий', self.run_easy)
        self.level_menu.add.button('Средний', self.run_medium)
        self.level_menu.add.button('Сложный', self.run_hard)
        self.level_menu.add.button('Супер сложный', self.run_super_hard)
        self.level_menu.add.button('Назад', self.run_menu)
        self.fast_pill_timer = 0

        # Фоновая музыка
        pygame.mixer.music.load('music.mp3')
        # Задаём громкость
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)


    def run_level_menu(self):
        """
        Запуск меню выбора уровня сложности
        :return:
        """
        self.level_menu.mainloop(self.display)

    def run_menu(self):
        """
        Меню игры
        :return:
        """
        self.menu.mainloop(self.display)

    def run_easy(self):
        """
        Запуск игры на лёгком уровне сложности
        :return:
        """
        self.difficulty = 1
        self.clock_speed = 6
        self.run()

    def run_medium(self):
        """
        Запуск игры на среднем уровне сложности
        :return:
        """
        self.difficulty = 2
        self.clock_speed = 7

        # Генерация случайных блоков
        self.blocks = []
        for i in range(20):
            self.blocks.append(Block(random.randint(0, self.width - 1), random.randint(0, self.height - 1)))

        blocks_to_remove = []
        # Удаление блоков из центра поля с радиусом 6
        for block in self.blocks:
            if abs(self.width // 2 - block.x) < 6 and abs(self.height // 2 - block.y) < 6:
                # Запоминай блоки, которые надо удалить
                blocks_to_remove.append(block)
        # Удаление блоков
        for block in blocks_to_remove:
            self.blocks.remove(block)

        # Генерация блоков по кругу вокруг поля
        for i in range(self.width):
            self.blocks.append(Block(i, 0))
            self.blocks.append(Block(i, self.height - 1))
        for i in range(self.height):
            self.blocks.append(Block(0, i))
            self.blocks.append(Block(self.width - 1, i))

        self.run()

    def run_hard(self):
        """
        Запуск игры на сложном уровне сложности
        :return:
        """
        self.difficulty = 3
        self.clock_speed = 9

        # Генерация стен
        self.blocks = []
        for i in range(15):
            # Выбираем направление стены
            direction = random.randint(0, 3)
            # Стартовая позиция стены
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            for lenght in range(random.randint(3, 10)):
                # С вероятностью 1 к 5 стена поворачивает
                if random.randint(0, 4) == 0:
                    direction = random.randint(0, 3)
                if direction == 0:
                    x += 1
                elif direction == 1:
                    x -= 1
                elif direction == 2:
                    y += 1
                elif direction == 3:
                    y -= 1
                self.blocks.append(Block(x, y))

        blocks_to_remove = []
        # Удаление блоков из центра поля с радиусом 6
        for block in self.blocks:
            if abs(self.width // 2 - block.x) < 6 and abs(self.height // 2 - block.y) < 6:
                # Запоминай блоки, которые надо удалить
                blocks_to_remove.append(block)
        # Удаление блоков
        for block in blocks_to_remove:
            self.blocks.remove(block)

        # Генерация блоков по кругу вокруг поля
        for i in range(self.width):
            self.blocks.append(Block(i, 0))
            self.blocks.append(Block(i, self.height - 1))
        for i in range(self.height):
            self.blocks.append(Block(0, i))
            self.blocks.append(Block(self.width - 1, i))
        self.run()

    def run_super_hard(self):
        """
        Запуск игры на супер сложном уровне сложности
        :return:
        """
        self.difficulty = 4
        self.clock_speed = 10

        self.blocks = []
        for i in range(50):
            # Выбираем направление стены
            direction = random.randint(0, 3)
            # Стартовая позиция стены
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            for length in range(random.randint(1, 5)):
                # С вероятностью 1 к 4 стена поворачивает
                if random.randint(0, 4) == 0:
                    direction = random.randint(0, 3)
                if direction == 0:
                    x += 1
                elif direction == 1:
                    x -= 1
                elif direction == 2:
                    y += 1
                elif direction == 3:
                    y -= 1
                self.blocks.append(Block(x, y))

        # Удаление блоков из списка, которые находятся внутри других блоков
        for block in self.blocks:
            for block2 in self.blocks:
                if block != block2 and block.x == block2.x and block.y == block2.y:
                    self.blocks.remove(block)
                    break

        blocks_to_remove = []
        # Удаление блоков из центра поля с радиусом 6
        for block in self.blocks:
            if abs(self.width // 2 - block.x) < 6 and abs(self.height // 2 - block.y) < 6:
                # Запоминай блоки, которые надо удалить
                blocks_to_remove.append(block)
        # Удаление блоков
        for block in blocks_to_remove:
            self.blocks.remove(block)

        # Генерация блоков по кругу вокруг поля
        for i in range(self.width):
            self.blocks.append(Block(i, 0))
            self.blocks.append(Block(i, self.height - 1))
        for i in range(self.height):
            self.blocks.append(Block(0, i))
            self.blocks.append(Block(self.width - 1, i))
        self.run()

    def run(self):
        """
        
        :return:
        """
        running = True  # Переменная для работы цикла
        clock = pygame.time.Clock()  # Создание часов
        self.snake = Snake(self.width // 2, self.height // 2)  # Создание змейки
        self.display.fill((0, 0, 0))  # Заливка экрана черным цветом
        self.regenerate_apple()  # Генерация яблока
        pygame.display.flip()

        while running:
            clock.tick(self.clock_speed)  # Установка частоты обновления экрана
            # Отрисовка блоков

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # Проверка на движение в противоположную сторону и длина змейки
                    if event.key == pygame.K_LEFT and (self.snake.direction != 'right' or self.snake.score == 0):
                        self.snake.direction = 'left'
                    elif event.key == pygame.K_RIGHT and (self.snake.direction != 'left' or self.snake.score == 0):
                        self.snake.direction = 'right'
                    elif event.key == pygame.K_UP and (self.snake.direction != 'down' or self.snake.score == 0):
                        self.snake.direction = 'up'
                    elif event.key == pygame.K_DOWN and (self.snake.direction != 'up' or self.snake.score == 0):
                        self.snake.direction = 'down'
                    # При нажатии на Esc выводит, вы действительно хотите выйти?
                    elif event.key == pygame.K_ESCAPE:
                        self.pause()

            self.display.fill((0, 0, 0))


            self.snake.move()

            # Проверка на столкновение с границами экрана и перенос змейки на другую сторону
            if self.snake.x > self.width - 1:
                self.snake.x = 0
            elif self.snake.x < 0:
                self.snake.x = self.width - 1
            elif self.snake.y > self.height - 1:
                self.snake.y = 0
            elif self.snake.y < 0:
                self.snake.y = self.height - 1

            # Проверка на столкновение с собой с учётом длины змейки
            for i in range(1, len(self.snake.body)):
                if self.snake.x == self.snake.body[i][0] and self.snake.y == self.snake.body[i][1]:
                    running = False

            # Проверка на столкновение с яблоком
            if self.snake.x == self.apple.x and self.snake.y == self.apple.y:

                # Если активна пилюля, то увеличиваем длину змейки на дополнительный блок
                if self.snake.is_pill(False):
                    self.snake.score += 1
                    self.snake.add_body()
                self.regenerate_apple()
                self.snake.add_body()

            # Проверка на столкновение с блоком
            for block in self.blocks:
                if self.snake.x == block.x and self.snake.y == block.y:
                    running = False

            # Проверка на столкновение с пилюлькой
            if self.pill:
                if self.snake.x == self.pill.x and self.snake.y == self.pill.y:
                    self.snake.eat_pill()
                    self.pill = None

            # Столкновение с быстрой пилюлькой
            if self.fast_pill:
                if self.snake.x == self.fast_pill.x and self.snake.y == self.fast_pill.y:
                    self.fast_pill = None
                    self.fast_pill_timer = 200
                    self.clock_speed *= 2

            # Проверка с таймером быстрой пилюли
            if self.fast_pill_timer > 0:
                self.fast_pill_timer -= 1
                if self.fast_pill_timer == 0:
                    self.clock_speed //= 2

            is_pill = self.snake.is_pill()
            # Отрисовка змейки
            for part in self.snake.body:
                if is_pill:
                    # Если змейка съела пилюлю, то она становится разноцветной со случайно генерируемы светлый оттенок
                    pygame.draw.rect(self.display,
                                     (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                                     (part[0] * self.block_size, part[1] * self.block_size, self.block_size,
                                      self.block_size))
                    # pygame.draw.rect(self.display,
                    #                  (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                    #                  (part[0] * self.block_size, part[1] * self.block_size, self.block_size,
                    #                   self.block_size))
                else:
                    pygame.draw.rect(self.display, (0, 255, 0), pygame.Rect(part[0] * 20, part[1] * 20, 20, 20))

            # Отрисовка блоков
            for block in self.blocks:
                block.draw(self.display)

            # Отрисовка яблока
            self.apple.draw(self.display)

            # Генерация и отрисовка пилюли
            if self.pill is None and random.randint(0, 100) == 0:
                self.generate_pill()
            elif self.pill is not None:
                self.pill.draw(self.display)

            # Быстрая пилуля
            if self.fast_pill is None and random.randint(0, 200) == 0 and self.fast_pill_timer == 0:
                self.generate_fast_pill()
            elif self.fast_pill:
                self.fast_pill.draw(self.display)

            # Отрисовка счёта
            value = self.font.render(f'Счёт: {self.snake.score}', True,
                                     (255, 255, 255))
            self.display.blit(value, (20, 20))

            # Если активна скоростная пилюля, то создаём синию окантовку вокруг поля
            if self.fast_pill_timer:
                pygame.draw.rect(self.display, (0, 191, 255),
                                 (0, 0, self.width * self.block_size, self.height * self.block_size), 3)

            # Перерисовка экрана
            pygame.display.flip()

        self.game_over()

    def regenerate_apple(self):
        """
        Генерация яблока
        :return:
        """
        # Проверка на то, что яблоко не появляется на змейке и не на блоке
        while True:
            self.apple.set_position(random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            for block in self.blocks:
                if self.apple.x != block.x and self.apple.y != block.y:
                    return
            if len(self.blocks) == 0:
                return

    def generate_pill(self):
        """
        Генерация пилюли
        :return:
        """

        # Проверка на то, что пилюля не появляется на змейке и не на блоке
        while True:
            self.pill = Pill(random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            for block in self.blocks:
                if self.pill.x != block.x and self.pill.y != block.y:
                    return
            if len(self.blocks) == 0:
                return

    def generate_fast_pill(self):
        """
        Генерация пилюли
        :return:
        """

        # Проверка на то, что пилюля не появляется на змейке и не на блоке
        while True:
            self.fast_pill = FastPill(random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            for block in self.blocks:
                if self.fast_pill.x != block.x and self.fast_pill.y != block.y:
                    return
            if len(self.blocks) == 0:
                return

    def show_records(self):
        """
        Отображение рекордов
        :return:
        """
        self.display.fill((0, 0, 0))
        value = self.font.render(f'Рекорды - Esc для выхода', True, (255, 255, 255))
        self.display.blit(value, (20, 20))
        # Получение рекордов из файла
        try:
            with open('records.txt', 'r') as file:
                records = file.readlines()
        except FileNotFoundError:
            records = []

        # Сортировка рекордов по убыванию
        records.sort(key=lambda x: int(x.split(' | ')[0]), reverse=True)

        # Отрисовка рекордов
        for i, record in enumerate(records):
            record = record.split(' | ')

            text = f'{i + 1}. Счёт: {record[0]} | '
            if record[1] == '1':
                text += 'Сложность: Легко'
            elif record[1] == '2':
                text += 'Сложность: Средне'
            elif record[1] == '3':
                text += 'Сложность: Сложно'
            elif record[1] == '4':
                text += 'Сложность: Очень сложно'

            # Время попытки
            text += f' | Время: {record[2][:-1]}'

            value = self.font.render(text, True, (255, 255, 255))
            self.display.blit(value, (20, 40 + i * 20))

        # Перерисовка экрана пока не нажмут на кнопку ESC
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
            pygame.display.flip()

    def game_over(self):
        """
        Выводит окно с сообщением о проигрыше
        :return:
        """

        self.display.fill((10, 10, 10))
        value = self.font.render(f'Игра окончена! Счёт: {self.snake.score}', True, (255, 255, 255))
        self.display.blit(value, (self.width * 20 // 2 - 100, self.height * 20 // 2 - 20))
        pygame.display.flip()

        # Сохранение рекорда в файл со временем и счётом и сложностью
        if self.snake.score > 0:
            with open('records.txt', 'a') as file:
                # Преобразуем время в формат дд.мм.гггг чч:мм:сс
                file.write(
                    f'{self.snake.score} | {self.difficulty} | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')

        # Перезапуск игры
        time.sleep(2)
        self.reset_game()

    def reset_game(self):
        """
        Сброс игры и возврат к начальному в главное меню
        :return:
        """
        self.blocks = []
        self.snake = None
        self.fast_pill_timer = 0
        self.snake = Snake(self.width // 2, self.height // 2)
        # Возврат в меню
        self.run_menu()

    def pause(self):
        """
        Выводит сообщение о том, что вы действительно хотите выйти
        А так же 2 кнопки с вариантами ответа
        Вернуться в игру / Выйти
        Enter - Выйти
        Esc - Вернуться в игру
        """
        pause = True
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pause = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause = False
                    elif event.key == pygame.K_RETURN:
                        self.game_over()

            self.display.fill((0, 0, 0))
            value = self.font.render('Вы действительно хотите выйти?', True, (255, 255, 255))
            value2 = self.font.render('Esc - Вернуться в игру   Enter - Выйти', True, (255, 255, 255))

            # Вывод сообщения по центру экрана
            self.display.blit(value, (self.width * 20 // 2 - 100, self.height * 20 // 2 - 20))
            self.display.blit(value2, (self.width * 20 // 2 - 110, self.height * 20 // 2 + 20))
            pygame.display.flip()


if __name__ == '__main__':
    game = Game(50, 40) # Размеры окна игры
    game.run_menu()
