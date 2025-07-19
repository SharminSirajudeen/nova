from dataclasses import dataclass
from typing import List, Optional, Any
from enum import Enum


class CommandType(str, Enum):
    """Types of commands NOVA can receive"""
    INTERACTIVE = "interactive"
    DIRECT = "direct"
    BACKGROUND = "background"
    STATUS = "status"
    MEMORY = "memory"
    HELP = "help"
    

@dataclass
class Command:
    """Parsed command from terminal"""
    type: CommandType
    content: Optional[str]
    args: List[str]
    options: dict[str, Any]
    
    @classmethod
    def from_args(cls, args: List[str]) -> "Command":
        """Parse command from CLI arguments"""
        if not args:
            return cls(CommandType.INTERACTIVE, None, [], {})
            
        # Check for special commands
        if "--background" in args:
            args.remove("--background")
            content = " ".join(args) if args else None
            return cls(CommandType.BACKGROUND, content, args, {"background": True})
            
        if "--status" in args:
            return cls(CommandType.STATUS, None, [], {})
            
        if "--memory" in args:
            return cls(CommandType.MEMORY, None, [], {})
            
        if "--help" in args or "-h" in args:
            return cls(CommandType.HELP, None, [], {})
            
        # Direct command
        content = " ".join(args)
        return cls(CommandType.DIRECT, content, args, {})
        

@dataclass
class CommandResult:
    """Result from command execution"""
    success: bool
    output: str
    error: Optional[str] = None
    actions_taken: List[str] = None
    
    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []