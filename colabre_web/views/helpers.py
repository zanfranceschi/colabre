is_not_verified_url = '/meu-perfil/solicitar-verificacao/'

def is_verified(user):
	return user.get_profile().is_verified


def not_from_oauth(user):
	return not user.get_profile().is_from_oauth
	