# create_3d_model.py

# import bpy
# import sys
# import os

# def create_3d_model_from_image(image_path, output_path):
#     # Загружаем изображение
#     img = bpy.data.images.load(image_path)

#     # Создаём плоскость
#     bpy.ops.mesh.primitive_plane_add(size=10)

#     # Загружаем текстуру
#     plane = bpy.context.object
#     mat = bpy.data.materials.new(name="TextureMaterial")
#     mat.use_nodes = True
#     bsdf = mat.node_tree.nodes["Principled BSDF"]
#     tex_image = mat.node_tree.nodes.new("ShaderNodeTexImage")
#     tex_image.image = img
#     mat.node_tree.links.new(bsdf.inputs["Base Color"], tex_image.outputs["Color"])

#     plane.data.materials.append(mat)

#     # Экспортируем модель в формате .obj
#     bpy.ops.export_scene.obj(filepath=output_path)

# if __name__ == "__main__":
#     # Получаем пути из аргументов командной строки
#     image_path = sys.argv[1]
#     output_path = sys.argv[2]
#     create_3d_model_from_image(image_path, output_path)
