# playstore-scraper-api
### WIP avoid TOO MANY REQUEST (429)
#### this project just the bridge between API and scraper lib from [https://github.com/doezaza12/playstore-scraper-api](https://github.com/JoMingyu/google-play-scraper)
#### you must add docker run --net=host when run this container (otherwise, docker default network will not be accessed eth1 from secondary ENI)
currently, hosting docker on amazon-linux-2 (default) is not stable, you have to schedule/manually restart docker when it starts ignore your request.
![udacity-datamodeling-scraper-api-strategy drawio](https://user-images.githubusercontent.com/45708687/209457355-caba991a-151e-4b34-883b-c46d1dd24201.png)
