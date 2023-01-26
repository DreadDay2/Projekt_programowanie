from ursina import *
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
app = Ursina()
Entity.default_shader = lit_with_shadows_shader

window.title = "Catch a sausage !"

# tworzenie podłoża mapy + gracza i broni
ground = Entity(model='plane', collider='mesh', scale=(70, 1, 70),
                texture='tx3.jpg', texture_scale=(4, 4))
                
player = FirstPersonController(
    model='cube', z=-10, color=color.orange, visible=False, origin_y=-.5, speed=9)
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

gun = Entity(model='AK-47.obj', parent=camera.ui,
             scale=0.24, color=color.black, on_cooldown=False, position=(0.5, -0.4),
             rotation=(15, 72, 5), texture='ak47.png')
gun.muzzle_flash = Entity(parent=gun, world_scale=.5,
                          model='AK-47.obj', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

# tworzenie mapy
wall = Entity(
    model='cube',
    # texture='wall',
    collider='box',
    scale=(70, 10, 4),
    position=(0, 5, 30),
    texture='wall.jpg',
)
wall2 = duplicate(wall, z=-30)
wall3 = duplicate(wall, rotation_y=90, x=-35, z=0)
wall4 = duplicate(wall3, x=35)
wall5 = duplicate(wall, position=(-20, 2, 15),
                  scale=(20, 5, 0.5))
wall6 = duplicate(wall, position=(-20, 2, -15),
                  scale=(20, 5, 0.5))
wall7 = duplicate(wall, position=(20, 2, 15),
                  scale=(20, 5, 0.5))
wall8 = duplicate(wall, position=(20, 2, -15),
                  scale=(20, 5, 0.5))
wall9 = duplicate(wall, position=(0, 2, 1), scale=(20, 5, 0.5))


def update():
    if held_keys['left mouse']:
        shoot()


def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5,
              wave='noise', pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)


class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale_y=3.5, scale_x=5,
                         origin_y=-.5, texture='sau.png', collider='box', **kwargs)
        self.health_bar = Entity(
            parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 90:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0),
                           self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 3:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

counter = 11
# Enemy()
for i in range(10):
    enemies = [Enemy(x=x*2) for x in range(1)]
    counter -= 1
while counter < 2:
    enemies = [Enemy(x=x*2) for x in range(10)]
    break
pause_handler = Entity(ignore_paused=True)
pause_text = Text('PAUSED', origin=(0,0), scale=2, enabled=False)

def pause_handler_input(key):
    if key == 'escape':
        application.paused = not application.paused 
        pause_text.enabled = application.paused     

pause_handler.input = pause_handler_input 

def update_2():
    if player.intersects(enemies).hit:
        print('ZGON')
        player.position = player.start_position


sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
Sky()
app.run()
