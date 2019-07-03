# expertease
This is the [MVP]() of the platform Expert-Ease: a [Telegram](https://en.wikipedia.org/wiki/Telegram_(software)) [bot](https://core.telegram.org/bots) that connects users of [Wordpress](https://wordpress.org/) to experts that help them in real time. :nerd_face:
The full story of how this venture came to life will is now published on [Medium](https://medium.com/@giladtsehori/storytime-from-idea-to-mvp-in-three-weeks-90699263be42)! Check it out.

## Table of contents:
 - [Introduction](#introduction)
 - [Why Telegram?](#why-telegram)
 - [Techy details](#techy-details)
 
 ## Introduction
 Users of many different [SAAS](https://en.wikipedia.org/wiki/Software_as_a_service) products and services have a hard time figuring out things on their own while using them for the first few times.
 Me and my team have seen this happen with multiple such products while researching the market, and have decided to tackle this problem by focusing on one platform: [Wordpress](https://en.wikipedia.org/wiki/WordPress) in our case, since the user base is large and the
 platform can be intimidating to new (or even intermediate) users.
 Moreover, we have decided at the point of the MVP to focus on only one platform to validate the [product-market fit](https://en.wikipedia.org/wiki/Product/market_fit) of the platform.
 
 
 During the phase of [market research](https://en.wikipedia.org/wiki/Market_research), we have conducted a survey with a little over a hundred participants, including professional web developers and influencers in
 the Israeli startup scene, which clearly showed that when people don't figure out the platforms, they first ask their friends and\or family or go
 to YouTube tutorials. This comes as surprise to none, as we can clearly see people abandoning the customer support channels that those platform offer; in our case, it was
 mostly because of long waiting time.
 
 This is where **Expert-Ease** comes in and addresses the problem; we wish to connect those users in search of support with experts on each platform, that will give them
 immediate, on-site, personal support with as little friction as possible. :star:
 
 ## Why Telegram?
 As said, I have decided to go on with a Telegram bot as an implementation for the MVP. The reason is, I had to make a working prototype in a relatively short period of time, so I
 needed to utilize an existing platform. Telegram seemed to have the simplest [API](https://core.telegram.org/) out of many platforms that can suffice, such as [Slack](https://api.slack.com/), [Whatsapp](https://www.whatsapp.com/business/api) and more. Furthermore, Telegram is highly reliable and being supported by an open community of developers, which makes it stand out.
 
 ## Techy details
Throughout structuring and developing *ExpertEaseBot*, I have run into many obstacles and challenges. This is one of my first 'big' Python project, in which I tried to implement best practices and 'Pythonic' code; coping with [PIP8](https://www.python.org/dev/peps/pep-0008/) rules, organizing a logical skeleton for the project (folders, packages etc), using diverse Python libraries (both from the [standard library](https://docs.python.org/3/library/) and 3rd party) and using [virtualenv](https://virtualenv.pypa.io/en/stable/) to create an local, isolated Python environment, that allowed me to work on ExpertEaseBot independent from other projects and repositories.
   
During the project, I incorporated some of [Git](https://git-scm.com/)'s main functionalities: initializing the git repository and pushing it remotely into GitHub, adding relevant parts to each commit, documenting all commits explicitly, branching, pull requesting, etc.

The project ran (and still runs...) on a cloud service; in my case, [Heroku](https://www.heroku.com/), and integrates with a SQL database, [PostgreSQL](https://www.postgresql.org/).

**Most used and vital libraries used in the project, along with the different technologies:**
- [*logging*](https://docs.python.org/3/library/logging.html) from the standard library. Since the application runs on the cloud constantly, it sometimes needs supervice. That's where the logger comes in: it allowed me to keep track of requests coming to the bot at all times, and catching errors allowed me to interact with the users directly in ease in order to fix immediate issues if necessary. This was all possible thanks to many logging statements, which can be time-consuming to implement but have the potential to save a huge headache later on. :relaxed:
- [*urllib*](https://docs.python.org/3/library/urllib.html) from the standard library, which was used with [psycopg2](https://www.google.com/search?q=psycopg2&oq=psycopg2&aqs=chrome..69i57j35i39l2j0l3.562j0j4&sourceid=chrome&ie=UTF-8). Those were used mainly to integrate with the PostgreSQL database on the cloud.
- [*telegram.ext*](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html) from the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) wrapper. This was used to interact with [Telegram's API](https://core.telegram.org/) indirectly.
- [*queue*](https://docs.python.org/3/library/queue.html) from the standard library. It was used to manage all incoming issues by users of the platform, to be handled by expert users in an orderly fashion. I used the synchronized queue for my implementation, as the bot works as a server (in some manner); it receives messages (aka requests) from different users and responds to them. The queue is one of the resources shared between all users of the program; thus it was implemented with [concurrency](https://en.wikipedia.org/wiki/Concurrency_(computer_science)) in mind.
