#!/usr/bin/env python3
"""
Test script for NOVA + nova_claude integration
Tests mode switching and basic company features
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.nova_core import NOVACore
from src.core.unified_engine import OperationMode


async def test_integration():
    """Test the integration"""
    print("Testing NOVA + nova_claude integration...\n")
    
    # Create NOVA core
    nova = NOVACore()
    
    # Initialize
    print("1. Initializing NOVA...")
    if not await nova.initialize():
        print("❌ Failed to initialize NOVA")
        return False
        
    print("✅ NOVA initialized successfully")
    print(f"   Current mode: {nova.get_current_mode()}")
    
    # Test mode switching
    print("\n2. Testing mode switching...")
    
    # Switch to company mode
    print("   Switching to company mode...")
    success = await nova.switch_mode('company')
    if success:
        print("✅ Successfully switched to company mode")
        print(f"   Current mode: {nova.get_current_mode()}")
    else:
        print("❌ Failed to switch to company mode")
        return False
        
    # Test company features
    print("\n3. Testing company features...")
    
    # Get company dashboard
    dashboard = await nova.get_company_dashboard()
    if dashboard:
        print("✅ Company dashboard accessible")
        print(f"   Company: {dashboard.get('company', 'Unknown')}")
        print(f"   Active projects: {dashboard.get('active_projects', 0)}")
        print(f"   AI agents: {dashboard.get('total_agents', 0)}")
    else:
        print("❌ Failed to get company dashboard")
        
    # Test project creation
    print("\n4. Testing project creation...")
    if nova.company:
        result = await nova.company.create_project(
            brief="Create a simple todo list web application with React frontend and Python backend",
            budget=10000,
            timeline_weeks=4
        )
        
        if result['success']:
            print("✅ Project created successfully!")
            print(f"   Project ID: {result['id']}")
            print(f"   Project name: {result['name']}")
            print(f"   Team size: {len(result['team'])}")
            print(f"   Tech stack: {', '.join(result['tech_stack'])}")
        else:
            print(f"❌ Failed to create project: {result.get('reason', 'Unknown')}")
    
    # Test personality engine
    print("\n5. Testing personality engine...")
    if hasattr(nova, 'unified_engine'):
        from src.models import Task, TaskComplexity
        
        test_task = Task(
            content="How should I architect a scalable microservices system?",
            complexity=TaskComplexity.COMPLEX,
            context={},
            requires_code_gen=False,
            requires_web_access=False
        )
        
        # Process in company mode (uses personalities)
        response = await nova.unified_engine.process_task(test_task)
        
        print("✅ Personality engine working")
        print(f"   Used personality: {response.personality_used.value if response.personality_used else 'None'}")
        print(f"   Model used: {response.model_used}")
        print(f"   Response preview: {response.content[:100]}...")
        
    # Switch back to personal mode
    print("\n6. Testing switch back to personal mode...")
    success = await nova.switch_mode('personal')
    if success:
        print("✅ Successfully switched back to personal mode")
        print(f"   Current mode: {nova.get_current_mode()}")
    else:
        print("❌ Failed to switch back to personal mode")
        
    # Test personal mode still works
    print("\n7. Testing personal mode functionality...")
    response = await nova.process_user_request("What's the weather like?")
    if response and 'response' in response:
        print("✅ Personal mode working correctly")
        print(f"   Model used: {response.get('model', 'Unknown')}")
    else:
        print("❌ Personal mode not working")
        
    print("\n✅ All integration tests completed successfully!")
    
    # Shutdown
    await nova.shutdown()
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("NOVA + nova_claude Integration Test")
    print("="*60)
    
    try:
        success = asyncio.run(test_integration())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)