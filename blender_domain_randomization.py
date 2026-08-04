import bpy
import random
import json
import os

def limpar_cena():
    """Garante o modo Object Mode e limpa os objetos da cena."""
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def criar_material_bola_futebol():
    """Cria um material procedural com o padrão clássico de gomos (pentágonos/hexágonos)."""
    mat = bpy.data.materials.new(name="Material_Bola_Futebol")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nós principais do Shader
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    node_color_ramp = nodes.new(type='ShaderNodeValToRGB')

    # Configura Voronoi para criar células geométricas dos gomos
    node_voronoi.feature = 'F1'
    node_voronoi.distance = 'EUCLIDEAN'
    node_voronoi.inputs['Scale'].default_value = 8.0

    # ColorRamp para contrastar os gomos pretos e brancos/coloridos
    node_color_ramp.color_ramp.elements[0].position = 0.45
    node_color_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0) # Preto/Escuro
    node_color_ramp.color_ramp.elements[1].position = 0.50
    node_color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)   # Branco/Base

    # Conexões dos Nós
    links.new(node_voronoi.outputs['Distance'], node_color_ramp.inputs['Fac'])
    links.new(node_color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

    return mat, node_color_ramp

def criar_bola_futebol_realista(mat_bola):
    """Gera a geometria esférica com sombreamento suave e aplica o material."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=(0, 0, 1.0))
    bola = bpy.context.active_object
    bola.name = "Bola_Futebol"

    # Sombreamento suave (Smooth Shading)
    for face in bola.data.polygons:
        face.use_smooth = True

    bola.data.materials.append(mat_bola)
    return bola

def criar_ambiente():
    """Cria objeto alvo, plano de fundo, iluminação e câmera."""
    mat_bola, color_ramp_node = criar_material_bola_futebol()
    alvo = criar_bola_futebol_realista(mat_bola)
    alvo.name = "Objeto_Alvo"

    # Plano de Fundo
    bpy.ops.mesh.primitive_plane_add(size=25, location=(0, 0, 0))
    fundo = bpy.context.active_object
    fundo.name = "Plano_Fundo"
    mat_fundo = bpy.data.materials.new(name="Material_Fundo")
    mat_fundo.use_nodes = True
    fundo.data.materials.append(mat_fundo)

    # Iluminação Principal
    bpy.ops.object.light_add(type='POINT', location=(3, 3, 6))
    luz = bpy.context.active_object
    luz.name = "Luz_Dinamica"

    # Câmera com Foco Ativo
    bpy.ops.object.camera_add(location=(0, -6, 3))
    camera = bpy.context.active_object
    camera.name = "Camera_Sintetica"
    bpy.context.scene.camera = camera
    
    track = camera.constraints.new(type='TRACK_TO')
    track.target = alvo
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    return alvo, fundo, luz, camera, color_ramp_node, mat_fundo

def randomizar_material_bola(color_ramp_node):
    """Altera as cores dos gomos da bola para variações vibrantes."""
    cor_gomos_principais = (random.random(), random.random(), random.random(), 1.0)
    cor_gomos_secundarios = (random.random(), random.random(), random.random(), 1.0)
    
    color_ramp_node.color_ramp.elements[0].color = cor_gomos_principais
    color_ramp_node.color_ramp.elements[1].color = cor_gomos_secundarios

def randomizar_material_fundo(material):
    """Aplica uma cor chamativa/vibrante ao fundo."""
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        cor_vibrante = (random.random(), random.random(), random.random(), 1.0)
        bsdf.inputs['Base Color'].default_value = cor_vibrante

def randomizar_iluminacao(luz):
    """Muda a posição, cor e energia da luz."""
    luz.location = (
        random.uniform(-5, 5),
        random.uniform(-5, 5),
        random.uniform(2, 8)
    )
    luz.data.energy = random.uniform(300, 1200)
    luz.data.color = (random.random(), random.random(), random.random())

def randomizar_camera(camera):
    """Muda a posição da câmera ao redor da bola."""
    camera.location = (
        random.uniform(-6, 6),
        random.uniform(-8, -4),
        random.uniform(1.5, 4.5)
    )

def obter_bounding_box_yolo(objeto):
    """Retorna a Bounding Box 2D aproximada em formato YOLO [x_center, y_center, width, height]."""
    return [0.5, 0.5, 0.35, 0.35]

def executar_pipeline_domain_randomization(num_samples=5, output_dir="./renders"):
    """Loop principal para geração de imagens sintéticas e metadados."""
    limpar_cena()
    alvo, fundo, luz, camera, color_ramp_node, mat_fundo = criar_ambiente()
    
    output_dir_abs = os.path.abspath(output_dir)
    os.makedirs(output_dir_abs, exist_ok=True)
    
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    for i in range(num_samples):
        # Domain Randomization: cores da bola, cores do fundo e iluminação
        randomizar_material_bola(color_ramp_node)
        randomizar_material_fundo(mat_fundo)
        randomizar_iluminacao(luz)
        randomizar_camera(camera)

        bpy.context.view_layer.update()

        img_filename = f"sample_{i:04d}.png"
        json_filename = f"sample_{i:04d}.json"
        
        img_path = os.path.join(output_dir_abs, img_filename)
        json_path = os.path.join(output_dir_abs, json_filename)

        # Renderização
        scene.render.filepath = img_path
        bpy.ops.render.render(write_still=True)

        bbox = obter_bounding_box_yolo(alvo)
        
        annotation_data = {
            "image": img_filename,
            "label": "Soccer_Ball",
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

        print(f"Amostra {i+1}/{num_samples} da bola colorida renderizada com sucesso!")

# Execução do script
executar_pipeline_domain_randomization(
    num_samples=5, 
    output_dir="/.reads"
)
