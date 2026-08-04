import bpy
import random
import json
import os
import mathutils

def limpar_cena():
    """Limpa objetos existentes na cena."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def criar_ambiente():
    """Cria objeto alvo, plano de fundo, luz e câmera."""
    # Objeto Principal (Alvo)
    bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 1))
    alvo = bpy.context.active_object
    alvo.name = "Objeto_Alvo"
    
    # Material dinâmico para o objeto
    mat_alvo = bpy.data.materials.new(name="Material_Alvo")
    mat_alvo.use_nodes = True
    alvo.data.materials.append(mat_alvo)

    # Plano de Fundo
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    fundo = bpy.context.active_object
    fundo.name = "Plano_Fundo"
    mat_fundo = bpy.data.materials.new(name="Material_Fundo")
    mat_fundo.use_nodes = True
    fundo.data.materials.append(mat_fundo)

    # Luz
    bpy.ops.object.light_add(type='POINT', location=(2, 2, 5))
    luz = bpy.context.active_object
    luz.name = "Luz_Dinamica"

    # Câmera
    bpy.ops.object.camera_add(location=(0, -6, 3))
    camera = bpy.context.active_object
    camera.name = "Camera_Sintetica"
    bpy.context.scene.camera = camera
    
    # Restrição para a câmera focar sempre no alvo
    track = camera.constraints.new(type='TRACK_TO')
    track.target = alvo
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    return alvo, fundo, luz, camera, mat_alvo, mat_fundo

def randomizar_material(material):
    """Aplica uma cor RGB aleatória ao material."""
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        cor_aleatoria = (random.random(), random.random(), random.random(), 1.0)
        bsdf.inputs['Base Color'].default_value = cor_aleatoria

def randomizar_iluminacao(luz):
    """Muda a posição, cor e energia da luz."""
    luz.location = (
        random.uniform(-5, 5),
        random.uniform(-5, 5),
        random.uniform(2, 8)
    )
    luz.data.energy = random.uniform(200, 1000)
    luz.data.color = (random.random(), random.random(), random.random())

def randomizar_camera(camera):
    """Muda a posição da câmera ao redor do objeto."""
    camera.location = (
        random.uniform(-7, 7),
        random.uniform(-9, -4),
        random.uniform(1, 5)
    )

def calcular_bounding_box_2d(scene, camera, objeto):
    """Calcula as coordenadas da Bounding Box 2D normalizadas (0 a 1)."""
    matrix = camera.matrix_world.inverted() @ objeto.matrix_world
    me = objeto.data
    coords = [matrix @ vertex.co for vertex in me.vertices]
    
    x_coords = []
    y_coords = []
    
    render = scene.render
    aspect_x = render.resolution_x
    aspect_y = render.resolution_y

    for coord in coords:
        co_2d = mathutils.geometry.box_pack_2d([coord])[1] if hasattr(mathutils.geometry, 'box_pack_2d') else None
        # Projeção simplificada de coordenadas normalizadas na tela
        proj = camera.calc_matrix_camera(
            depsgraph=bpy.context.evaluated_depsgraph_get(),
            x=aspect_x, y=aspect_y
        ) @ mathutils.Vector((coord.x, coord.y, coord.z, 1.0))
        
        if proj.w != 0:
            x = (proj.x / proj.w + 1.0) / 2.0
            y = (proj.y / proj.w + 1.0) / 2.0
            x_coords.append(min(max(x, 0.0), 1.0))
            y_coords.append(min(max(y, 0.0), 1.0))

    if not x_coords or not y_coords:
        return [0.5, 0.5, 0.2, 0.2] # Fallback

    xmin, xmax = min(x_coords), max(x_coords)
    ymin, ymax = min(y_coords), max(y_coords)
    
    # Formato YOLO: [x_center, y_center, width, height]
    x_center = (xmin + xmax) / 2.0
    y_center = (ymin + ymax) / 2.0
    width = xmax - xmin
    height = ymax - ymin

    return [x_center, y_center, width, height]

def executar_pipeline_domain_randomization(num_samples=10, output_dir="./renders"):
    """Loop principal para geração de imagens sintéticas e metadados."""
    limpar_cena()
    alvo, fundo, luz, camera, mat_alvo, mat_fundo = criar_ambiente()
    
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    for i in range(num_samples):
        # Apply Domain Randomization
        randomizar_material(mat_alvo)
        randomizar_material(mat_fundo)
        randomizar_iluminacao(luz)
        randomizar_camera(camera)

        bpy.context.view_layer.update()

        # Configura caminho de saída da imagem
        img_filename = f"sample_{i:04d}.png"
        json_filename = f"sample_{i:04d}.json"
        
        img_path = os.path.join(output_dir, img_filename)
        json_path = os.path.join(output_dir, json_filename)

        scene.render.filepath = img_path
        bpy.ops.render.render(write_still=True)

        # Extrai Ground Truth / Bounding Box
        bbox = calcular_bounding_box_2d(scene, camera, alvo)
        
        annotation_data = {
            "image": img_filename,
            "label": "Suzanne_Monkey",
            "bbox_yolo_format": {
                "x_center": bbox[0],
                "y_center": bbox[1],
                "width": bbox[2],
                "height": bbox[3]
            },
            "light_energy": luz.data.energy,
            "camera_location": list(camera.location)
        }

        with open(json_path, 'w') as f:
            json.dump(annotation_data, f, indent=4)

        print(f"Sample {i+1}/{num_samples} gerada com sucesso!")

# Execução do Script
if __name__ == "__main__":
    executar_pipeline_domain_randomization(num_samples=5, output_dir="./renders")
