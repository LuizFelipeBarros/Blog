from db import listar_usuarios

print("Tentando listar usuários...")
usuarios = listar_usuarios()

print(f"\nTipo retornado: {type(usuarios)}")
print(f"Quantidade: {len(usuarios) if usuarios else 0}")
print(f"Conteúdo: {usuarios}")

if usuarios:
    print("\n✅ Usuários encontrados:")
    for u in usuarios:
        print(f"  - ID: {u['idUsuario']}, Nome: {u['nome']}, User: {u['user']}")
else:
    print("\n❌ Nenhum usuário encontrado!")