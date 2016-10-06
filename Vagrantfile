# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "precise64"

    config.vm.network "forwarded_port", guest: 8000, host: 8000

    config.vm.provision "shell", inline: <<-SHELL
        apt-get update
        apt-get install curl -q -y
        curl -sL https://deb.nodesource.com/setup_6.x | bash -
        apt-get install python-dev python-pip openjdk-7-jre-headless nodejs ruby-sass libjpeg-dev -q -y
        npm install -g coffee-script
        pip install -r /vagrant/requirements.txt
    SHELL
end
