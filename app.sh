COMMAND=$1
STAGE=$2
APP_NAME=$3
APP_VERSION=$4

if [ "$COMMAND" != "create" -a "$COMMAND" != "build" -a "$COMMAND" != "run" -a "$COMMAND" != "push" -a "$COMMAND" != "update" -a "$COMMAND" != "delete" ] || [ "$STAGE" != "devo" -a "$STAGE" != "gamma" -a "$STAGE" != "prod" ] || [ "$APP_NAME" == "" ] || [ "$APP_VERSION" == "" ]
then
  echo "syntax: bash build-app.sh <command> <stage> <app-name> <app-version>"
  exit 0
fi



if [ $STAGE == "devo" ]
then
  AWS_PROJ_ID="381780986962"
  VPC_ID="vpc-662a5602"
  LB_LISTNER="arn:aws:elasticloadbalancing:ap-southeast-1:381780986962:listener/app/devo-lb-pvt/9063c6c4e264ea17/33322206f52c31c4"
elif [ $STAGE == "gamma" ]
then
  AWS_PROJ_ID="370531249777"
  VPC_ID="vpc-c13c7da5"
  LB_LISTNER="arn:aws:elasticloadbalancing:ap-southeast-1:370531249777:listener/app/gamma-lb-pvt/98bfeb8d67ee2d26/a854c15563502db0"
elif [ $STAGE == "prod" ]
then
  AWS_PROJ_ID="370531249777"
  VPC_ID="vpc-c13c7da5"
  LB_LISTNER="arn:aws:elasticloadbalancing:ap-southeast-1:370531249777:listener/app/prod-lb-pvt/bfbfa36e82445261/0104e43e491b57f8"
fi

ECR_REPO=$AWS_PROJ_ID.dkr.ecr.ap-southeast-1.amazonaws.com/$STAGE
ECR_IMAGE=$ECR_REPO/$APP_NAME:$APP_VERSION



if [ $COMMAND == "create" ]
then

  cat Dockerfile.raw \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    > Dockerfile
  cat ecr-task-def.raw \
    | sed "s#\$STAGE#$STAGE#g" \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    | sed "s#\$APP_NAME#$APP_NAME#g" \
    | sed "s#\$APP_VERSION#$APP_VERSION#g" \
    > ecr-task-def.json

  aws ecr create-repository --repository-name $STAGE/$APP_NAME >> /dev/null 2>&1
  echo ... create ecr repository: $STAGE/$APP_NAME

  TARGET_GRP=$(aws elbv2 create-target-group \
    --name ecs-$STAGE-$APP_NAME-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-interval-seconds 15 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 5 \
    --unhealthy-threshold-count 2 \
    --matcher HttpCode=200)
  TARGET_GRP_ARN=$(echo $TARGET_GRP | grep -Po '"TargetGroupArn": "\K[^"]+')
  echo ... created target group: $TARGET_GRP_ARN

  aws elbv2 create-rule \
    --listener-arn $LB_LISTNER \
    --priority $(date +%M)$(date +%H) \
    --conditions Field=path-pattern,Values=\'/$APP_NAME*\' \
    --actions Type=forward,TargetGroupArn=$TARGET_GRP_ARN >> /dev/null 2>&1
  echo ... added target group to the internal load balancer
  
  sudo docker build --tag $ECR_IMAGE .
  echo ... built docker image: $ECR_IMAGE
  
  sudo $(aws ecr get-login)
  sudo docker push $ECR_IMAGE
  echo ... pushed docker image: $ECR_IMAGE

  TASK_DEF=$(aws ecs register-task-definition --cli-input-json file://ecr-task-def.json)
  TASK_DEF_VER=$(echo $TASK_DEF | grep -Po '"revision": \K[0-9]+')
  echo ... created task definition: $APP_NAME:$TASK_DEF_VER

  aws ecs create-service \
    --cluster $STAGE-ecs \
    --service-name $APP_NAME \
    --task-definition $APP_NAME:$TASK_DEF_VER \
    --role ecsServiceRole \
    --load-balancers targetGroupArn=$TARGET_GRP_ARN,containerName=$APP_NAME,containerPort=80 \
    --desired-count 1 >> /dev/null 2>&1
  echo ... created service: $APP_NAME

  rm Dockerfile
  rm ecr-task-def.json

elif [ $COMMAND == "build" ]
then

  cat Dockerfile.raw \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    > Dockerfile
  sudo docker build --tag $ECR_IMAGE .
  rm Dockerfile

elif [ $COMMAND == "run" ]
then

  cat Dockerfile.raw \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    > Dockerfile
  sudo docker build --tag $ECR_IMAGE .
  rm Dockerfile
  sudo docker run $ECR_IMAGE

elif [ $COMMAND == "push" ]
then

  cat Dockerfile.raw \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    > Dockerfile
  cat ecr-task-def.raw \
    | sed "s#\$STAGE#$STAGE#g" \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    | sed "s#\$APP_NAME#$APP_NAME#g" \
    | sed "s#\$APP_VERSION#$APP_VERSION#g" \
    > ecr-task-def.json
  sudo docker build --tag $ECR_IMAGE .
  sudo $(aws ecr get-login)
  sudo docker push $ECR_IMAGE
  aws ecs register-task-definition --cli-input-json file://ecr-task-def.json
  rm Dockerfile
  rm ecr-task-def.json

elif [ $COMMAND == "update" ]
then

  cat Dockerfile.raw \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    > Dockerfile
  cat ecr-task-def.raw \
    | sed "s#\$STAGE#$STAGE#g" \
    | sed "s#\$DOCKER_REPO#$ECR_REPO#g" \
    | sed "s#\$APP_NAME#$APP_NAME#g" \
    | sed "s#\$APP_VERSION#$APP_VERSION#g" \
    > ecr-task-def.json
  sudo docker build --tag $ECR_IMAGE .
  sudo $(aws ecr get-login)
  sudo docker push $ECR_IMAGE
  TASK_DEF_VER=$(aws ecs register-task-definition --cli-input-json file://ecr-task-def.json | grep -Eo '"revision": *[0-9]+' | grep -Eo [0-9]+)
  aws ecs update-service \
    --cluster $STAGE-ecs \
    --service $APP_NAME \
    --task-definition $APP_NAME:$TASK_DEF_VER
  rm Dockerfile
  rm ecr-task-def.json

elif [ $COMMAND == "delete" ]
then

  aws ecs update-service --cluster pratilipi-$STAGE-ecs --service $APP_NAME --desired-count 0
  aws ecs delete-service --cluster pratilipi-$STAGE-ecs --service $APP_NAME

fi
