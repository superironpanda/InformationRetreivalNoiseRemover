from noise_remover import NoiseRemover

url = "https://www.foxbusiness.com/politics/what-trump-pick-amy-coney-barrett-could-mean-for-future-of-the-supreme-court"
noise_remover = NoiseRemover()
noise_remover.remove_noise(url, "spanish")
