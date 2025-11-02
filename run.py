import multiprocessing


def startJarvis():
        # Code for process 1
        print("Process 1 is running.")
        from assistant import start
        start()


if __name__ == '__main__':
        p1 = multiprocessing.Process(target=startJarvis)

        p1.start()

        p1.join()


        print("system stop") 