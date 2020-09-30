from noise_remover import NoiseRemover

url = "https://techcrunch.com/2020/09/30/online-garden-shop-bloomscape-raises-15m-series-b-acquires-plant-care-app-vera/"
noise_remover = NoiseRemover()
noise_remover.remove_noise(url, "english")
