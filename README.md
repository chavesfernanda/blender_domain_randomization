# Generation of Synthetic Datasets via Domain Randomization in Blender

Este repositório contém uma solução avançada em Python (`bpy`) para geração automatizada de datasets sintéticos com **Domain Randomization** e extração de rótulos (*Ground Truth*) para modelos de Visão Computacional / IA.

## Recursos Implementados
1. **Randomização de Iluminação:** Variação dinâmica de intensidade, cor e posição da fonte de luz a cada frame.
2. **Randomização de Materiais:** Alteração automática de cores e propriedades BSDF nos materiais do objeto e do fundo.
3. **Variabilidade de Câmera:** Mudança de ângulo e distância focal com rastreamento ativo (`Track To Constraint`).
4. **Exportação de Ground Truth:** Cálculo de Bounding Box 2D em formato YOLO/JSON para cada imagem renderizada.

## Estrutura do Repositório
- `blender_domain_randomization.py`: Notebook com o script completo e documentado.
- `/renders`: Pasta com amostras das imagens sintéticas `.png` e seus respectivos metadados `.json`.
- `README.md`: Documentação e pipeline de testes.

## Exemplo de Anotação Gerada (`.json`)
```json
{
    "image": "sample_0000.png",
    "label": "Suzanne_Monkey",
    "bbox_yolo_format": {
        "x_center": 0.512,
        "y_center": 0.489,
        "width": 0.310,
        "height": 0.285
    }
}
