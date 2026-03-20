docker container rm VivaanXop -f > /dev/null
sleep 2
echo "Starting and Deploying MecoMusic"
docker run -d --restart=always --name VivaanXop VivaanXop
