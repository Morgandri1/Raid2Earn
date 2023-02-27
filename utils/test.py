import ed25519

private_key = b'your-private-key-here'
public_key = ed25519.publickey(private_key)

print("Public key:", public_key.to_bytes())