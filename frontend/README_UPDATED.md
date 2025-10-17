# 📻 Radio Oriente FM - Frontend

## 🎯 Overview

Modern React frontend for Radio Oriente FM, fully integrated with the normalized SQLite backend. Features a responsive design, real-time radio streaming, and comprehensive content management.

## ✨ Features

### 🎵 **Radio Streaming**
- Live radio streaming with custom player
- Volume control and mute functionality
- Stream URL management from backend
- Audio context for global playback state

### 📝 **Content Management**
- **Unified Articles System**: Combined news and blog functionality
- **Programming Schedule**: Dynamic program listings with schedules
- **Contact Forms**: Multi-type contact system with validation
- **Band Registration**: Comprehensive emerging artist application system
- **Newsletter Subscription**: Email subscription management

### 🔐 **Authentication**
- User registration and login
- Token-based authentication
- Profile management
- Protected routes and forms

### 🌐 **Location Integration**
- Country, city, and commune selection
- Dynamic location loading
- Hierarchical location relationships

### 📱 **Responsive Design**
- Mobile-first approach
- Tablet and desktop optimized
- Touch-friendly interfaces
- Modern CSS Grid and Flexbox layouts

## 🛠 Technology Stack

- **React 18** - Modern React with hooks
- **React Router 6** - Client-side routing
- **Axios** - HTTP client with interceptors
- **React Hot Toast** - Toast notifications
- **Lucide React** - Modern icon library
- **CSS3** - Custom styling with CSS Grid/Flexbox

## 📁 Project Structure

```
src/
├── components/          # Reusable components
│   ├── Navbar.js       # Navigation component
│   ├── RadioPlayer.js  # Radio streaming player
│   ├── LiveChat.js     # Chat functionality
│   ├── Footer.js       # Footer component
│   └── Emergente.js    # Band registration form
├── pages/              # Page components
│   ├── Home.js         # Homepage
│   ├── Articles.js     # Unified news/blog page
│   ├── Programming.js  # Radio programming
│   ├── Contact.js      # Contact form
│   ├── Subscription.js # Newsletter subscription
│   ├── Login.js        # User login
│   └── Register.js     # User registration
├── contexts/           # React contexts
│   ├── AuthContext.js  # Authentication state
│   └── AudioContext.js # Audio player state
├── layouts/            # Layout components
│   ├── LayoutPrincipal.js
│   └── LayoutPantallaCompleta.js
├── utils/              # Utility functions
│   ├── api.js          # API configuration
│   └── constants.js    # App constants
└── App.js              # Main application component
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Clone and install dependencies**
```bash
cd frontend
npm install
```

2. **Environment Setup**
Create `.env` file:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STREAM_URL=https://sonic-us.fhost.cl/8126/stream
```

3. **Start Development Server**
```bash
npm start
```

4. **Build for Production**
```bash
npm run build
```

## 🔌 API Integration

### **Endpoints Used**

#### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `GET /api/auth/profile/` - Get user profile

#### Content
- `GET /api/blog/articulos/` - Get articles
- `GET /api/blog/categorias/` - Get categories
- `GET /api/radio/api/programas/` - Get programs
- `GET /api/radio/api/horarios/` - Get schedules

#### Forms
- `POST /api/contact/contactos/` - Submit contact form
- `POST /api/contact/suscripciones/` - Newsletter subscription
- `POST /api/emergente/bandas/` - Band registration

#### Location
- `GET /api/ubicacion/paises/` - Get countries
- `GET /api/ubicacion/ciudades/` - Get cities
- `GET /api/ubicacion/comunas/` - Get communes

### **API Configuration**

The app uses a centralized API configuration in `src/utils/api.js`:

```javascript
import { contactAPI, radioAPI, blogAPI } from './utils/api';

// Usage example
const articles = await blogAPI.getArticulos();
const genres = await radioAPI.getGeneros();
```

## 🎨 Styling

### **CSS Architecture**
- Component-scoped CSS files
- Shared styles in `App.css` and `index.css`
- CSS custom properties for theming
- Responsive design with mobile-first approach

### **Key CSS Files**
- `App.css` - Global styles and layout
- `Pages.css` - Shared page styles
- `components/*.css` - Component-specific styles

## 📱 Components

### **Core Components**

#### **RadioPlayer**
- Global audio player with context
- Volume control and mute
- Stream URL from backend
- Expandable player interface

#### **Navbar**
- Responsive navigation
- Authentication state aware
- Active route highlighting
- Mobile hamburger menu

#### **Articles (Unified News/Blog)**
- Category filtering
- Search functionality
- Featured articles
- Modal article view
- Responsive grid layout

#### **Contact Form**
- Dynamic contact types
- Real-time validation
- Station information integration
- Authentication support

#### **Emergente (Band Registration)**
- Multi-step form experience
- Dynamic integrante management
- Social media links handling
- File upload support
- Location selection

## 🔐 Authentication Flow

1. **Login/Register** → Token stored in localStorage
2. **API Requests** → Token automatically added to headers
3. **Token Expiry** → Automatic logout and redirect
4. **Protected Routes** → Authentication check before access

## 📊 State Management

### **Contexts Used**

#### **AuthContext**
```javascript
const { user, login, logout, isAuthenticated } = useAuth();
```

#### **AudioContext**
```javascript
const { isPlaying, togglePlay, volume, setVolume } = useContext(AudioContextGlobal);
```

## 🎯 Key Features Implementation

### **Unified Articles System**
- Combines news and blog functionality
- Category-based filtering
- Search across all content
- Featured articles highlighting
- Modal view for full articles

### **Enhanced Band Registration**
- Dynamic integrante list management
- Multiple social media links
- Genre and location selection
- Document upload support
- Real-time validation

### **Smart Contact System**
- Dynamic contact type loading
- Real station information display
- Context-aware form behavior
- Authentication integration

### **Responsive Programming Display**
- Day-based schedule organization
- Program and conductor information
- Time formatting and display
- Mobile-optimized layout

## 🚨 Error Handling

### **Global Error Handling**
- API interceptors for common errors
- Toast notifications for user feedback
- Fallback data for offline scenarios
- Graceful degradation

### **Form Validation**
- Real-time field validation
- Custom validation rules
- User-friendly error messages
- Accessibility compliance

## 🔧 Development Tools

### **Available Scripts**
- `npm start` - Development server
- `npm run build` - Production build
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### **Development Features**
- Hot reloading
- Error boundary
- Development warnings
- Performance monitoring

## 🌟 Best Practices

### **Code Organization**
- Component composition over inheritance
- Custom hooks for reusable logic
- Context for global state
- Utility functions for common operations

### **Performance**
- Lazy loading for routes
- Optimized re-renders
- Efficient API calls
- Image optimization

### **Accessibility**
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

## 🚀 Deployment

### **Build Process**
```bash
npm run build
```

### **Environment Variables**
- `REACT_APP_API_URL` - Backend API URL
- `REACT_APP_STREAM_URL` - Radio stream URL

### **Production Considerations**
- API URL configuration
- CORS settings
- Static file serving
- Error monitoring

## 📈 Future Enhancements

### **Planned Features**
- [ ] Progressive Web App (PWA)
- [ ] Offline functionality
- [ ] Push notifications
- [ ] Advanced search
- [ ] User preferences
- [ ] Social media integration
- [ ] Analytics dashboard

### **Technical Improvements**
- [ ] TypeScript migration
- [ ] Testing suite expansion
- [ ] Performance optimization
- [ ] Bundle size reduction
- [ ] SEO improvements

## 🤝 Contributing

1. Follow React best practices
2. Use consistent naming conventions
3. Add proper error handling
4. Include responsive design
5. Test on multiple devices
6. Document new features

## 📞 Support

For technical support or questions:
- Check the backend API documentation
- Review component documentation
- Test API endpoints independently
- Verify authentication flow

---

**Radio Oriente FM Frontend** - Connecting music lovers with great content! 🎵
