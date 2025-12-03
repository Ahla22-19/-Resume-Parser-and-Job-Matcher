import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper,
  IconButton,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import SearchIcon from '@mui/icons-material/Search';
import WorkIcon from '@mui/icons-material/Work';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = 'http://localhost:8000';

const JobChatbot = ({ resumeData, sessionId, onReset }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [jobSuggestions, setJobSuggestions] = useState([]);
  const [expandedJob, setExpandedJob] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize chat with greeting
    const initChat = async () => {
      setLoading(true);
      try {
        const response = await axios.post(`${API_BASE_URL}/chat/${sessionId}`, {
          role: 'user',
          content: 'hello'
        });

        const newMessage = {
          id: Date.now(),
          role: 'assistant',
          content: response.data.message,
          jobSuggestions: response.data.job_suggestions || []
        };

        setMessages([newMessage]);
        if (response.data.job_suggestions) {
          setJobSuggestions(response.data.job_suggestions);
        }
      } catch (error) {
        console.error('Failed to initialize chat:', error);
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      initChat();
    }
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/${sessionId}`, {
        role: 'user',
        content: inputMessage
      });

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.message,
        jobSuggestions: response.data.job_suggestions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.data.job_suggestions && response.data.job_suggestions.length > 0) {
        setJobSuggestions(response.data.job_suggestions);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        jobSuggestions: []
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = async (action) => {
    let message = '';
    switch (action) {
      case 'search_jobs':
        message = 'Find me job opportunities matching my skills';
        break;
      case 'resume_feedback':
        message = 'Give me feedback on my resume';
        break;
      case 'career_advice':
        message = 'What career advice do you have for me?';
        break;
      default:
        return;
    }

    setInputMessage(message);
  };

  const renderMessageContent = (content) => {
    return (
      <ReactMarkdown
        components={{
          a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2' }} />
          ),
          strong: ({ node, ...props }) => (
            <strong {...props} style={{ fontWeight: 'bold' }} />
          )
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SmartToyIcon /> Job Hunter Assistant
            </Typography>
            <Button variant="outlined" color="secondary" onClick={onReset}>
              Upload New Resume
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" paragraph>
            Chat with your AI job hunting assistant. I'll help you find opportunities matching your resume.
          </Typography>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Resume Skills
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, justifyContent: 'center', mt: 1 }}>
                  {resumeData.skills.slice(0, 3).map((skill, index) => (
                    <Chip key={index} label={skill} size="small" />
                  ))}
                  {resumeData.skills.length > 3 && (
                    <Chip label={`+${resumeData.skills.length - 3}`} size="small" />
                  )}
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Experience
                </Typography>
                <Typography variant="h6">
                  {resumeData.experience.length} positions
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Session
                </Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {sessionId?.substring(0, 8)}...
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={<SearchIcon />}
              onClick={() => handleQuickAction('search_jobs')}
              size="small"
            >
              Find Jobs
            </Button>
            <Button
              variant="outlined"
              onClick={() => handleQuickAction('resume_feedback')}
              size="small"
            >
              Resume Feedback
            </Button>
            <Button
              variant="outlined"
              onClick={() => handleQuickAction('career_advice')}
              size="small"
            >
              Career Advice
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, overflow: 'auto' }}>
              <List sx={{ width: '100%' }}>
                {messages.map((message) => (
                  <ListItem
                    key={message.id}
                    sx={{
                      flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                      alignItems: 'flex-start',
                      mb: 2
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main' }}>
                        {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Paper
                          sx={{
                            p: 2,
                            maxWidth: '70%',
                            bgcolor: message.role === 'user' ? 'primary.light' : 'grey.100',
                            color: message.role === 'user' ? 'white' : 'text.primary',
                            borderRadius: 2
                          }}
                        >
                          {renderMessageContent(message.content)}
                        </Paper>
                      }
                      sx={{
                        ml: message.role === 'user' ? 0 : 2,
                        mr: message.role === 'user' ? 2 : 0,
                        textAlign: message.role === 'user' ? 'right' : 'left'
                      }}
                    />
                  </ListItem>
                ))}
                {loading && (
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'secondary.main' }}>
                        <SmartToyIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Paper sx={{ p: 2, maxWidth: '70%' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CircularProgress size={20} />
                            <Typography>Thinking...</Typography>
                          </Box>
                        </Paper>
                      }
                    />
                  </ListItem>
                )}
                <div ref={messagesEndRef} />
              </List>
            </CardContent>
            
            <Divider />
            
            <CardContent>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Type your message here..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                  multiline
                  maxRows={3}
                />
                <IconButton
                  color="primary"
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || loading}
                  sx={{ alignSelf: 'flex-end' }}
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '500px', overflow: 'auto' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <WorkIcon /> Job Suggestions
              </Typography>
              
              {jobSuggestions.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No job suggestions yet. Try asking "Find me jobs" or "Search for opportunities".
                </Typography>
              ) : (
                <Box>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Found {jobSuggestions.length} matching jobs
                  </Alert>
                  
                  {jobSuggestions.map((job, index) => (
                    <Accordion
                      key={index}
                      expanded={expandedJob === index}
                      onChange={() => setExpandedJob(expandedJob === index ? null : index)}
                      sx={{ mb: 1 }}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ width: '100%' }}>
                          <Typography variant="subtitle2" fontWeight="bold">
                            {job.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {job.company} • {job.location}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                            <Chip 
                              label={`${Math.round(job.match_score * 100)}% match`} 
                              size="small" 
                              color={job.match_score > 0.7 ? 'success' : job.match_score > 0.4 ? 'warning' : 'default'}
                            />
                            <Typography variant="caption">
                              {job.posted_date || 'Recently'}
                            </Typography>
                          </Box>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" paragraph>
                          {job.description}
                        </Typography>
                        {job.salary && (
                          <Typography variant="body2" fontWeight="bold" color="primary" gutterBottom>
                            Salary: {job.salary}
                          </Typography>
                        )}
                        <Button
                          variant="contained"
                          size="small"
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          fullWidth
                        >
                          View Job
                        </Button>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default JobChatbot;