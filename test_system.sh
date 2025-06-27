#!/bin/bash
# AppBinHub Test Runner
# Quick verification of the automation system

echo "AppBinHub System Test Runner"
echo "============================"

# Check if we're in the right directory
if [ ! -f "scripts/monitor.py" ]; then
    echo "❌ Error: Run this script from the AppBinHub root directory"
    exit 1
fi

# Run Python verification
echo "Running Python verification..."
cd scripts
python verify_system.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 System verification completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Set up GitHub repository and secrets"
    echo "2. Push code to GitHub"
    echo "3. Enable GitHub Actions and Pages"
    echo "4. Test workflows manually"
else
    echo ""
    echo "❌ System verification failed!"
    echo "Please fix the issues above before deployment."
fi

exit $exit_code
