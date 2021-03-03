import time
import schedule
import subprocess

from datetime import datetime


def runner():
    print(f'{datetime.utcnow()} ||| Work started!')

    """Monday"""
    schedule.every().monday.at("12:50").do(docker_prune_system)
    schedule.every().monday.at("12:51").do(docker_prune_container)
    schedule.every().monday.at("12:52").do(docker_prune_image)
    schedule.every().monday.at("12:53").do(docker_prune_network)
    schedule.every().monday.at("12:54").do(docker_prune_volume)
    schedule.every().monday.at("12:55").do(docker_ps)
    schedule.every().monday.at("12:56").do(docker_stop)
    schedule.every().monday.at("12:57").do(docker_rm)
    schedule.every().monday.at("12:58").do(docker_rmi)
    schedule.every().monday.at("13:00").do(build)
    schedule.every().monday.at("14:01").do(start)

    """Wednesday"""
    schedule.every().wednesday.at("12:50").do(docker_prune_system)
    schedule.every().wednesday.at("12:51").do(docker_prune_container)
    schedule.every().wednesday.at("12:52").do(docker_prune_image)
    schedule.every().wednesday.at("12:53").do(docker_prune_network)
    schedule.every().wednesday.at("12:54").do(docker_prune_volume)
    schedule.every().wednesday.at("12:55").do(docker_ps)
    schedule.every().wednesday.at("12:56").do(docker_stop)
    schedule.every().wednesday.at("12:57").do(docker_rm)
    schedule.every().wednesday.at("12:58").do(docker_rmi)
    schedule.every().wednesday.at("13:00").do(build)
    schedule.every().wednesday.at("14:01").do(start)

    """Friday"""
    schedule.every().friday.at("12:50").do(docker_prune_system)
    schedule.every().friday.at("12:51").do(docker_prune_container)
    schedule.every().friday.at("12:51").do(docker_prune_image)
    schedule.every().friday.at("12:53").do(docker_prune_network)
    schedule.every().friday.at("12:54").do(docker_prune_volume)
    schedule.every().friday.at("12:55").do(docker_ps)
    schedule.every().friday.at("12:56").do(docker_stop)
    schedule.every().friday.at("12:57").do(docker_rm)
    schedule.every().friday.at("12:58").do(docker_rmi)
    schedule.every().friday.at("13:00").do(build)
    schedule.every().friday.at("14:01").do(start)

    while True:
        schedule.run_pending()
        time.sleep(1)
        # print(datetime.utcnow())


def docker_prune_system():
    subprocess.run('docker system prune -f', shell=True)
    print(f'{datetime.utcnow()} ||| docker system prune -f')


def docker_prune_container():
    subprocess.run('docker container prune -f', shell=True)
    print(f'{datetime.utcnow()} ||| docker container prune -f')


def docker_prune_image():
    subprocess.run('docker image prune -f', shell=True)
    print(f'{datetime.utcnow()} ||| docker image prune -f')


def docker_prune_network():
    subprocess.run('docker network prune -f', shell=True)
    print(f'{datetime.utcnow()} ||| docker network prune -f')


def docker_prune_volume():
    subprocess.run('docker volume prune -f', shell=True)
    print(f'{datetime.utcnow()} ||| docker volume prune -f')


def docker_ps():
    subprocess.run('docker ps -aq', shell=True)
    print(f'{datetime.utcnow()} ||| docker ps -aq')


def docker_stop():
    subprocess.run('docker stop $(docker ps -aq)', shell=True)
    print(f'{datetime.utcnow()} ||| docker stop $(docker ps -aq)')


def docker_rm():
    subprocess.run('docker rm $(docker ps -aq)', shell=True)
    print(f'{datetime.utcnow()} ||| docker rm $(docker ps -aq)')


def docker_rmi():
    subprocess.run('docker rmi $(docker images -q)', shell=True)
    print(f'{datetime.utcnow()} ||| docker rmi $(docker images -q)')


def build():
    subprocess.run('make build', shell=True)
    print(f'{datetime.utcnow()} ||| make build')


def start():
    subprocess.run('make celery', shell=True)
    print(f'{datetime.utcnow()} ||| make celery')


if __name__ == '__main__':
    runner()
