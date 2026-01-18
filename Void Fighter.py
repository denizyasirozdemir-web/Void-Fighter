from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random, math

app = Ursina(borderless=False)
Entity.default_shader = lit_with_shadows_shader
mouse.locked = True



# ---------------- PLAYER ----------------
ship = Entity(
    model='assets/spaceship.glb',  # kendi gemin
    scale=20,
    position=(0,0,0),
    collider=None
)

camera.parent = ship
camera.position = (0, 10, -20)
camera.rotation = (10, 0, 0)

speed = 10
mouse_sensitivity = Vec2(40, 40)

velocity = Vec3(0,0,0)
move_force = 12
damping = 0.92
mouse_sens = 45
oxygen = 10000
inside_station = False

Sky(color=color.black)
DirectionalLight(rotation=(45,45,45))

ui = Text("", position=(-0.85,0.45), scale=2)

# ---------------- GUN ----------------
gun = Entity(
    parent=camera.ui,   # ← camera DEĞİL
    model='assets/sci_fi_gun.glb',
    position=(0.35, -0.15),
    scale=0.25,
    rotation=(0,180,0),
    always_on_top=True
)





print(load_model('assets/space_station.glb'))
print(load_model('assets/spaceship.glb'))

# ---------------- ASTEROIDS ----------------
asteroids = []
for _ in range(20):
    asteroids.append(Entity(
        model='sphere',
        scale=random.uniform(1.5,3),
        position=(random.uniform(-40,40),
                  random.uniform(-40,40),
                  random.uniform(20,80)),
        color=color.gray,
        collider='sphere'
    ))

model = Entity(
    model='assets/sci_fi_space_station.glb',
    scale=2,
    color=color.azure,
    collider='mesh',
    position = (0,0,0),
)

npc = Entity(
    model='assets/autonomous_quadruped_radar_heavy.glb',
    scale=1.5,
    position=(5, 2, 8),
    collider='box'
)

npc = Entity(
    model='assets/rusty_spaceship.glb',
    scale=1.5,
    position=(-3, 5, 12),
    collider='box'
)

npc = Entity(
    model='assets/spaceship.glb',
    scale=1.5,
    position=(-3, 5, -12),
    collider='box'
)

npc = Entity(
    model='assets/spaceship_santa.glb',
    scale=1.5,
    position=(-3, 15, 23),
    collider='box'
)

npc_text = Text(
    text='',
    scale=2,
    background=True
)

npc_float_offset = random.random() * 10

def npc_update():
    global npc_float_offset
    npc_update()

    # NPC gemiye baksın
    npc.look_at(ship)
    npc.rotation_x = 0
    npc.rotation_z = 0

    # Uzayda süzülme efekti
    npc.y = 2 + math.sin(time.time() + npc_float_offset) * 0.5

    # Mesafe kontrolü
    dist = distance(ship.position, npc.position)

    if dist < 10:
        npc_text.text = "E bas → Sinyal al"
        npc_text.position = (0, -0.35)
    else:
        npc_text.text = ""

def input(key):
    if key == 'left mouse down':
        Bullet(gun.world_position, camera.forward)
        gun.animate_position(gun.position + Vec3(0,0,-0.1), 0.05)
        gun.animate_position(gun.position, 0.05, delay=0.05)

    if key == 'e':
        if distance(ship.position, npc.position) < 10:
            npc_text.text = "📡 Drone: İstasyonda anomali tespit edildi."
            invoke(clear_npc_text, delay=3)

def clear_npc_text():
    npc_text.text = ""

print(load_model('assets/models/antonomus_quadruped_radar_heavy.glb'))


# ---------------- BULLET ----------------
class Bullet(Entity):
    def __init__(self, pos, direction):
        super().__init__(
            model='sphere',
            scale=0.08,
            color=color.yellow,
            position=pos,
            collider='sphere'
        )
        self.dir = direction
        self.life = 2

    def update(self):
        self.position += self.dir * time.dt * 40
        self.life -= time.dt
        if self.life <= 0:
            destroy(self)

        for e in enemies:
            if self.intersects(e).hit:
                e.take_damage()
                destroy(self)
                break

def input(key):
    if key == 'left mouse down':
        Bullet(gun.world_position, camera.forward)
        gun.animate_position(gun.position + Vec3(0,0,-0.1), 0.05)
        gun.animate_position(gun.position, 0.05, delay=0.05)

# ---------------- EXPLOSION ----------------
def explosion(pos):
    e = Entity(model='sphere', scale=0.2, position=pos, color=color.orange)
    e.animate_scale(3, duration=0.2)
    e.animate_color(color.clear, duration=0.2)
    destroy(e, delay=0.25)

# ---------------- ENEMY ----------------
enemies = []

class BlockEnemy(Entity):
    def __init__(self, pos):
        super().__init__(
            model='cube',
            color=color.red,
            scale=1.2,
            position=pos,
            collider='box'
        )
        self.hp = 3
        self.t = random.random()*10

    def update(self):
        self.t += time.dt*6
        self.y = 1 + math.sin(self.t)*0.3
        self.look_at(ship)
        self.position += self.forward * time.dt * 1.2

        if self.intersects(ship).hit:
            global oxygen
            oxygen -= 20

    def take_damage(self):
        self.hp -= 1
        self.animate_scale(1.5, 0.1)
        self.animate_scale(1.2, 0.1, delay=0.1)

        if self.hp <= 0:
            explosion(self.position)
            enemies.remove(self)
            destroy(self)

# ---------------- STATION INSIDE ----------------
inside_blocks = []

def build_station_inside():
    global inside_station
    inside_station = True

    for b in inside_blocks:
        destroy(b)
    inside_blocks.clear()

    for e in enemies:
        destroy(e)
    enemies.clear()

    for x in range(-5,6):
        for z in range(-5,6):
            inside_blocks.append(Entity(
                model='cube',
                position=(x,-1,z),
                color=color.dark_gray,
                collider='box'
            ))

    for _ in range(5):
        enemies.append(BlockEnemy(
            Vec3(random.randint(-4,4),1,random.randint(-4,4))
        ))

# ---------------- DOOR ----------------
door = Entity(
    model='cube',
    scale=(2,3,0.3),
    position=(0,1.5,6),
    color=color.azure,
    collider='box'
)
door_open = False
door_hint = Text("", y=-0.4, scale=2)

# ---------------- SUN + PLANET ----------------
sun = Entity(model='sphere', scale=20, position=(200,100,300), color=color.yellow)
DirectionalLight(parent=sun, rotation=(45,-30,0), shadows=True)

planet = Entity(model='sphere', scale=40, position=(-300,-100,600), texture='earth', double_sided=True)
Entity(parent=planet, model='sphere', scale=1.05, color=color.azure.tint(0.4), transparency=True)

# ---------------- STATIONS ----------------
stations = []
for _ in range(3):
    stations.append(Entity(
        model='cube',
        scale=(12,6,12),
        position=(random.randint(-80,80),
                  random.randint(-40,40),
                  random.randint(60,120)),
        color=color.light_gray,
        collider='box'
    ))

# ---------------- UPDATE ----------------
def update():
    global velocity, oxygen, door_open

    sun.rotation_y += time.dt * 2

    # Mouse look
    ship.rotation_y += mouse.velocity[0] * mouse_sens
    camera.rotation_x -= mouse.velocity[1] * mouse_sens
    camera.rotation_x = clamp(camera.rotation_x, -85, 85)

    # Movement
    direction = Vec3(
        held_keys['d'] - held_keys['a'],
        held_keys['space'] - held_keys['shift'],
        held_keys['w'] - held_keys['s']
    )

    if direction.length() > 0:
        direction = (
            ship.right * direction.x +
            ship.up * direction.y +
            ship.forward * direction.z
        ).normalized()
        velocity += direction * move_force * time.dt

    ship.position += velocity * time.dt
    velocity *= damping

    # Oxygen
    oxygen -= time.dt * 2
    ui.text = f"Oksijen: {int(oxygen)}"
    if oxygen <= 0:
        application.quit()

    # Station entry
    if not inside_station:
        for s in stations:
            if ship.intersects(s).hit:
                ship.position = (0,2,0)
                velocity = Vec3(0,0,0)
                build_station_inside()
                break

def update():
    global speed

    move_dir = Vec3(
        held_keys['d'] - held_keys['a'],
        held_keys['space'] - held_keys['left shift'],
        held_keys['w'] - held_keys['s']
    )

    ship.position += ship.forward * move_dir.z * speed * time.dt
    ship.position += ship.right * move_dir.x * speed * time.dt
    ship.position += ship.up * move_dir.y * speed * time.dt

    ship.rotation_y += mouse.velocity[0] * mouse_sensitivity.x
    ship.rotation_x -= mouse.velocity[1] * mouse_sensitivity.y
    ship.rotation_x = clamp(ship.rotation_x, -80, 80)


    # Door
    if inside_station and ship.intersects(door).hit:
        door_hint.text = "E bas → Kapıyı aç"
        if held_keys['e'] and not door_open:
            door.animate_y(4, duration=0.5)
            door_open = True
            door_hint.text = ""
    else:
        door_hint.text = ""


app.run()
