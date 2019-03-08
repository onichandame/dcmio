# git Instruction

The best friend of collaborative teamwork

## Concept

git is designed to help control the versioning of softwares(VCS). <https://git-scm.com/book/en/v1/Getting-Started-About-Version-Control> is the man page of git.

## What Is Version in Git?

git is able to track almost all actions conducted during software development.

![alt text](https://git-scm.com/figures/18333fig0104-tn.png)

As shown in above picture, git stores changed files at checkin. A version is composed of the changed files and pointers to the unchanged files. In this way, git provides the possibility to revert to old versions. In git's manpage, the jargon meaning "version" is "snapshot".

## Significance

The adoption of git to our work has 2 main reasons:
1. **Registration of TPS require a record of the developement process.** 
Keeping records from the first day is better than taking the risk of frauding.
2. **Git is a tool made for collaboration.**
The first author if git is the father of Linux. The whole purpose is to make it easier for the Linux developers around the world to collaborate more efficiently

## Difficulties

Due to the fact that the authors and the maintainers of git are primarily Linux advocates, git is very much biased towards the Linux users. However, there is an officially supported version of git which runs on Windows. As for the more difficult part on the server-side, I have cleaned all the dirt with no problem.

## How to Use Git on Windows

First, one needs to download git beforing installing it. The following is a download link from the official site.
<https://git-scm.com/download/win>

Second, one needs to install it before doing configuration. Double-click the downloaded file and follow all the way through. Keep the default settings during installation.

At this stage you should be able to find "Git Bash" and "Git GUI" in *START* menu.

Launch "Git GUI" and you should see 3 links. "Repository" here stands for the "project". As I have set up a server which hosts the *dcmio* project, you should click the link "Clone Existing Repository".

In the popped window there are 2 fields to be filled and 3 exclusive options. Don't fill in any field yet because I need to grant you the access to the server. Before I can do this, I will need you to provide a "key" to me.

Look at the option bar with "Repository" and "Help". Choose "Help", In the dropdown menu, click "Show SSH Key". In the popped window, click "generate key". Now you should see a very long string appearing in the text box. Send me everything in the text box through email and wait until I finish the server-side authentication process.

With everythin set, type in the first field named "Source Location": ssh://git@221.231.235.34:10086/dcmio

Type in the other field any location where you want to store the downloaded code. NOTE: manually add "/dcmio" at the end of the field. e.g. After you have selected the path "C:\your\path", change it to "C:\your\path\dcmio"

Among the options, choose "Full Copy".

Now you have finished all the configuration. You are free to click "clone" and wait until *dcmio* is downloaded. During your wait, in case a window pops up you need to type in "yes" followed by Enter.

Don't panic, this process needs to be done only once, unless you have lost your copy of *dcmio*

If everything went well, you should now have a copy of *dcmio* written by me in the location you specified.

## Branch on Windows

The good thing about git is that it makes branching very easy. A branch is simply a pointer to a chosen version. When a new version is created, only 1 pointer will automatically move along to the latest version. All other pointers stays where they were until it is explicitly told to move.

The simplest application of branch is using `master` and `development` branches. In this way, the `master` branch stays untouched until the development branch is well tested and validated.

The example is *dcmio*. Since the validation of the first version of the code, I have frozen the `master` branch until now. When I started re-working the data structure of dcmio, I created another branch called `dev`. All modification are saved to this branch. The obvious benefit is that I can mess up my own branch while keeping the `master` branch unchanged.

In the case of *dcmio*, The `master` branch stays where the most recently validated version is. the `dev` branch keeps the track of my recent work including the re-work.

Enough wording, now I will introduce the method to get different version from the git server.

1. Every time you download from the server, you get all the information and all the branches. Therefore you need to download the lastest information of branches

2. In case you don't remember how to download from the server,

   * launch **Git GUI**

   * In 'Open Recent Repository' section choose *dcmio*

   * in the toolbar select **Remote**

   * select **Fetch from** then **origin**

   * Wait until success then close the popped window

3. Now the branching starts:

   * in the toolbar select **Branch** then **checkout**

   * select 'Tracking Branch' and you can see a list of 'origin/\*' items. These are branch fetched from the server

   * Choose 'origin/dev' then **Checkout**. Now you are at a remote branch. git is designed to store everythin locally, so you need to make a local branch now

   * Again go to **Branch** then **Create**

   * Fill in a name of your choice. Select 'This Detached Checkout' then **Create**

   * Now the local branch has been created and you should checkout to this new local branch

   * Go to **Branch** then **Create**

   * select 'Local Branch' then **Checkout**

4. Now go to the folder where *dcmio* is stored and you have the latest developing version of branch `dev`
