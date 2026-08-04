import bpy
import random
import json
import os

def limpar_cena():
    """Garante o modo Object Mode e limpa os objetos da cena."""
    # Se houver um objeto ativo e estiver em Edit Mode (ou outro), força voltar para Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Seleciona todos os objetos e os deleta
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

def obter_bounding_box_yolo(objeto):
    """Retorna uma Bounding Box 2D aproximada em formato YOLO [x_center, y_center, width, height]."""
    # Exemplo formatado padrão de Bounding Box normalizada
    return [0.5, 0.5, 0.35, 0.35]

def executar_pipeline_domain_randomization(num_samples=5, output_dir="./renders"):
    """Loop principal para geração de imagens sintéticas e metadados."""
    limpar_cena()
    alvo, fundo, luz, camera, mat_alvo, mat_fundo = criar_ambiente()
    
    # Garante o caminho absoluto da pasta renders
    output_dir_abs = os.path.abspath(output_dir)
    os.makedirs(output_dir_abs, exist_ok=True)
    
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    for i in range(num_samples):
        # Aplica Domain Randomization
        randomizar_material(mat_alvo)
        randomizar_material(mat_fundo)
        randomizar_iluminacao(luz)
        randomizar_camera(camera)

        bpy.context.view_layer.update()

        # Nomes dos arquivos de saída
        img_filename = f"sample_{i:04d}.png"
        json_filename = f"sample_{i:04d}.json"
        
        img_path = os.path.join(output_dir_abs, img_filename)
        json_path = os.path.join(output_dir_abs, json_filename)

        # Renderização da imagem
        scene.render.filepath = img_path
        bpy.ops.render.render(write_still=True)

        # Geração dos metadados
        bbox = obter_bounding_box_yolo(alvo)
        
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

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, indent=4)

        print(f"Amostra {i+1}/{num_samples} renderizada com sucesso!")

# Execução do script edite de acordo com o caminho de execução do seu repositorio
# o meu em questão foi (home/fernanda/Documents/Documentos/Fastcamp - Dados Sintéticos/blender_domain_randomization/renders)
executar_pipeline_domain_randomization(num_samples=5, output_dir="./renders")
