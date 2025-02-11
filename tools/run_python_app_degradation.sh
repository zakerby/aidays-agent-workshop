# Parse arguments
while getopts "c:m:h" opt; do
    case $opt in
        c)
            CONTAINER_NAME=$OPTARG
        ;;
        m)
            MODE=$OPTARG
        ;;
        h)
            echo "Usage: $0 -p <container> -m <mode>"
            echo "Options:"
            echo "  -c <container>  Container name"
            echo "  -m <mode>       Values available: random, cpu, memory, network"
            exit 1
        ;;
        \?)
        echo "Invalid option: -$OPTARG" >&2
        ;;
    esac
done

# Check if container is provided
if [ -z "$CONTAINER_NAME" ]; then
    echo "Container is not provided"
    echo "Using default container: webapp"
    CONTAINER_NAME="webapp"
fi

# Check if mode is provided
if [ -z "$MODE" ]; then
    echo "Mode is not provided"
    echo "Using default mode: random"
    MODE="random"
fi

# If mode is CPU or Memory, check if duration is provided
if [ "$MODE" == "cpu" ] || [ "$MODE" == "memory" ]; then
    if [ -z "$DURATION" ]; then
        echo "Duration is not provided"
        echo "Using default duration: 60 seconds"
        DURATION=60
    fi
fi

# CPU or Memory case
if [ "$MODE" == "cpu" ] || [ "$MODE" == "memory" ]; then
    echo "Degrading performance of container $CONTAINER_NAME with mode $MODE for $DURATION seconds"
    python degrade_performance.py --container $CONTAINER --mode $MODE --duration $DURATION
else
    echo "Degrading performance of container $CONTAINER_NAME with mode $MODE"
    python degrade_performance.py --container $CONTAINER --mode $MODE
fi